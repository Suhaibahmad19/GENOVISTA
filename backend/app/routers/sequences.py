from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import uuid
import gzip
import shutil
import re
from typing import List

# create a router object
router = APIRouter()

# directory to store sequence files
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Pydantic model for incoming sequence data
class SequenceUpload(BaseModel):
    sequence: str

@router.get("/")
def list_sequences():
    """
    List available DNA sequences stored in the data folder.
    Returns id, preview (first bases), length, and whether a compressed file exists.
    """
    items = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".txt"):
            path = os.path.join(DATA_DIR, file)
            # support both legacy id_name.txt and new id.txt
            filename_no_ext = file[:-4]
            if "_" in filename_no_ext:
                seq_id = filename_no_ext.split("_", 1)[0]
            else:
                seq_id = filename_no_ext
            # read to get length
            try:
                with open(path, "r") as f:
                    sequence = f.read().strip().upper()
                length = len(sequence)
                preview = sequence[:20] + ("..." if length > 20 else "")
            except Exception:
                length = None
                preview = None
            # compressed exists?
            compressed_exists = os.path.exists(path + ".gz")
            items.append({
                "id": seq_id,
                "preview": preview,
                "length": length,
                "compressed": compressed_exists
            })
    # sort by newest first (by file mtime desc)
    def mtime_for(item):
        # prefer new pattern id.txt; fallback to any matching legacy file
        path_new = os.path.join(DATA_DIR, f"{item['id']}.txt")
        if os.path.exists(path_new):
            return os.path.getmtime(path_new)
        # find any file starting with id_
        for f in os.listdir(DATA_DIR):
            if f.startswith(item['id'] + "_") and f.endswith('.txt'):
                return os.path.getmtime(os.path.join(DATA_DIR, f))
        return 0
    items.sort(key=mtime_for, reverse=True)
    return {"items": items}

@router.post("/")
def upload_sequence(payload: SequenceUpload):
    """
    Upload a new DNA sequence and store it as a .txt file
    """
    # generate a unique ID for the sequence
    seq_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(DATA_DIR, f"{seq_id}.txt")

    # simple validation
    seq = payload.sequence.upper()
    if not all(base in "ATCG" for base in seq):
        raise HTTPException(status_code=400, detail="Invalid DNA sequence. Use only A, T, C, G.")

    # write to file
    with open(file_path, "w") as f:
        f.write(seq)

    return {
        "id": seq_id,
        "length": len(seq),
        "message": "Sequence uploaded successfully"
    }

@router.get("/{seq_id}")
def get_sequence(seq_id: str):
    """
    Return the full stored DNA sequence for a given id and its length.
    Supports both new pattern `id.txt` and legacy `id_*.txt`.
    """
    # try new pattern first
    candidate = os.path.join(DATA_DIR, f"{seq_id}.txt")
    sequence_file = None
    if os.path.exists(candidate):
        sequence_file = candidate
    else:
        # search legacy
        for f in os.listdir(DATA_DIR):
            if f.startswith(seq_id + "_") and f.endswith('.txt'):
                sequence_file = os.path.join(DATA_DIR, f)
                break

    if not sequence_file:
        raise HTTPException(status_code=404, detail="Sequence file not found for this ID.")

    with open(sequence_file, "r") as f:
        sequence = f.read().strip().upper()

    return {
        "id": seq_id,
        "sequence": sequence,
        "length": len(sequence)
    }

class SequenceUpdate(BaseModel):
    sequence: str

@router.put("/{seq_id}")
def update_sequence(seq_id: str, payload: SequenceUpdate):
    """
    Replace the stored DNA sequence for a given id (overwrites .txt, removes old .gz if exists).
    Supports both new pattern `id.txt` and legacy `id_*.txt`; will write back to `id.txt`.
    """
    # ensure data dir
    os.makedirs(DATA_DIR, exist_ok=True)

    # remove any legacy txts for this id
    for f in os.listdir(DATA_DIR):
        if (f == f"{seq_id}.txt") or (f.startswith(seq_id + "_") and f.endswith('.txt')):
            try:
                os.remove(os.path.join(DATA_DIR, f))
            except FileNotFoundError:
                pass

    # write new sequence
    seq = payload.sequence.upper()
    if not all(base in "ATCG" for base in seq):
        raise HTTPException(status_code=400, detail="Invalid DNA sequence. Use only A, T, C, G.")
    path_new = os.path.join(DATA_DIR, f"{seq_id}.txt")
    with open(path_new, 'w') as f:
        f.write(seq)

    # remove any gz for this id (since content changed)
    gz_new = path_new + '.gz'
    if os.path.exists(gz_new):
        try:
            os.remove(gz_new)
        except FileNotFoundError:
            pass
    # also remove any legacy gz
    for f in os.listdir(DATA_DIR):
        if f.startswith(seq_id) and f.endswith('.gz'):
            try:
                os.remove(os.path.join(DATA_DIR, f))
            except FileNotFoundError:
                pass

    return {"id": seq_id, "length": len(seq), "message": "Sequence updated successfully"}

@router.delete("/{seq_id}")
def delete_sequence(seq_id: str):
    """
    Delete the stored DNA sequence (both .txt and any .gz) for a given id.
    """
    found = False
    # delete txts
    for f in os.listdir(DATA_DIR):
        if (f == f"{seq_id}.txt") or (f.startswith(seq_id + "_") and f.endswith('.txt')):
            try:
                os.remove(os.path.join(DATA_DIR, f))
                found = True
            except FileNotFoundError:
                pass
    # delete gz
    for f in os.listdir(DATA_DIR):
        if f.startswith(seq_id) and f.endswith('.gz'):
            try:
                os.remove(os.path.join(DATA_DIR, f))
            except FileNotFoundError:
                pass
    if not found:
        raise HTTPException(status_code=404, detail="Sequence file not found for this ID.")
    return {"id": seq_id, "message": "Sequence deleted"}

@router.post("/{seq_id}/compress")
def compress_sequence(seq_id: str):
    """
    Compress the stored DNA sequence using gzip (lossless compression)
    """
    # find the file in data folder
    original_file = None
    for file in os.listdir(DATA_DIR):
        if file.startswith(seq_id):
            original_file = os.path.join(DATA_DIR, file)
            break

    if not original_file:
        raise HTTPException(status_code=404, detail="Sequence ID not found.")

    compressed_file = f"{original_file}.gz"

    # compress the file
    with open(original_file, "rb") as f_in:
        with gzip.open(compressed_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    # get sizes
    original_size = os.path.getsize(original_file)
    compressed_size = os.path.getsize(compressed_file)

    return {
        "id": seq_id,
        "original_size_bytes": original_size,
        "compressed_size_bytes": compressed_size,
        "compression_ratio": round(compressed_size / original_size, 3),
        "message": "Sequence compressed successfully",
        "compressed_file": os.path.basename(compressed_file)
    }

@router.get("/{seq_id}/decompress")
def decompress_sequence(seq_id: str):
    """
    Decompress a gzip-compressed DNA sequence and verify lossless reconstruction.
    """
    # locate compressed and original files
    original_file = None
    compressed_file = None

    for file in os.listdir(DATA_DIR):
        if file.startswith(seq_id) and file.endswith(".txt"):
            original_file = os.path.join(DATA_DIR, file)
        elif file.startswith(seq_id) and file.endswith(".gz"):
            compressed_file = os.path.join(DATA_DIR, file)

    if not compressed_file:
        raise HTTPException(status_code=404, detail="Compressed file not found for this ID.")

    # decompress content
    with gzip.open(compressed_file, "rb") as f_in:
        decompressed_data = f_in.read().decode("utf-8")

    # optional: verify against original (if exists)
    lossless = False
    if original_file and os.path.exists(original_file):
        with open(original_file, "r") as f_orig:
            original_data = f_orig.read()
        lossless = (original_data == decompressed_data)

    return {
        "id": seq_id,
        "sequence_preview": decompressed_data[:100] + ("..." if len(decompressed_data) > 100 else ""),
        "length": len(decompressed_data),
        "lossless_verification": lossless,
        "message": "Decompression completed successfully"
    }
@router.get("/{seq_id}/gc")
def calculate_gc_content(seq_id: str):
    """
    Calculate GC content (percentage of G and C bases) for a stored DNA sequence.
    """
    # find the original file
    sequence_file = None
    for file in os.listdir(DATA_DIR):
        if file.startswith(seq_id) and file.endswith(".txt"):
            sequence_file = os.path.join(DATA_DIR, file)
            break

    if not sequence_file:
        raise HTTPException(status_code=404, detail="Sequence file not found for this ID.")

    # read the sequence
    with open(sequence_file, "r") as f:
        sequence = f.read().upper()

    if len(sequence) == 0:
        raise HTTPException(status_code=400, detail="Sequence file is empty.")

    # compute counts
    g_count = sequence.count("G")
    c_count = sequence.count("C")
    gc_content = round(((g_count + c_count) / len(sequence)) * 100, 3)

    return {
        "id": seq_id,
        "length": len(sequence),
        "G_count": g_count,
        "C_count": c_count,
        "GC_percent": gc_content,
        "message": "GC content calculated successfully"
    }
@router.get("/{seq_id}/freq")
def nucleotide_frequency(seq_id: str):
    """
    Calculate frequency (count and percentage) of each nucleotide (A, T, C, G)
    in a stored DNA sequence.
    """
    # find the file
    sequence_file = None
    for file in os.listdir(DATA_DIR):
        if file.startswith(seq_id) and file.endswith(".txt"):
            sequence_file = os.path.join(DATA_DIR, file)
            break

    if not sequence_file:
        raise HTTPException(status_code=404, detail="Sequence file not found for this ID.")

    # read the sequence
    with open(sequence_file, "r") as f:
        sequence = f.read().upper()

    if len(sequence) == 0:
        raise HTTPException(status_code=400, detail="Sequence file is empty.")

    # count nucleotides
    bases = ["A", "T", "C", "G"]
    counts = {b: sequence.count(b) for b in bases}
    total = len(sequence)
    percentages = {b: round((counts[b] / total) * 100, 3) for b in bases}

    return {
        "id": seq_id,
        "length": total,
        "counts": counts,
        "percentages": percentages,
        "message": "Nucleotide frequency calculated successfully"
    }

from typing import List

class MotifRequest(BaseModel):
    pattern: str
    use_regex: bool = False

@router.post("/{seq_id}/motif")
def search_motif(seq_id: str, payload: MotifRequest):
    """
    Search for a DNA motif or regex pattern in a stored sequence.
    Returns match positions and matched sequences.
    """
    # locate file
    sequence_file = None
    for file in os.listdir(DATA_DIR):
        if file.startswith(seq_id) and file.endswith(".txt"):
            sequence_file = os.path.join(DATA_DIR, file)
            break

    if not sequence_file:
        raise HTTPException(status_code=404, detail="Sequence file not found for this ID.")

    # read sequence
    with open(sequence_file, "r") as f:
        sequence = f.read().upper()

    if len(sequence) == 0:
        raise HTTPException(status_code=400, detail="Sequence file is empty.")

    pattern = payload.pattern.upper()

    # if regex enabled
    if payload.use_regex:
        try:
            matches = list(re.finditer(pattern, sequence))
        except re.error:
            raise HTTPException(status_code=400, detail="Invalid regex pattern.")
    else:
        # simple literal search
        matches = []
        start = 0
        while True:
            idx = sequence.find(pattern, start)
            if idx == -1:
                break
            matches.append({"start": idx + 1, "end": idx + len(pattern), "match": pattern})
            start = idx + 1

    # if regex mode used, extract matches
    if payload.use_regex:
        formatted_matches = [
            {"start": m.start() + 1, "end": m.end(), "match": m.group()} for m in matches
        ]
    else:
        formatted_matches = matches

    return {
        "id": seq_id,
        "pattern": payload.pattern,
        "use_regex": payload.use_regex,
        "total_matches": len(formatted_matches),
        "matches": formatted_matches,
        "message": "Motif search completed successfully"
    }

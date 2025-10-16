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
    name: str
    sequence: str

@router.post("/")
def upload_sequence(payload: SequenceUpload):
    """
    Upload a new DNA sequence and store it as a .txt file
    """
    # generate a unique ID for the sequence
    seq_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(DATA_DIR, f"{seq_id}_{payload.name}.txt")

    # simple validation
    seq = payload.sequence.upper()
    if not all(base in "ATCG" for base in seq):
        raise HTTPException(status_code=400, detail="Invalid DNA sequence. Use only A, T, C, G.")

    # write to file
    with open(file_path, "w") as f:
        f.write(seq)

    return {
        "id": seq_id,
        "name": payload.name,
        "length": len(seq),
        "message": "Sequence uploaded successfully"
    }

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

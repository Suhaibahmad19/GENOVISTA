# GENOVISTA

Minimal, user-friendly platform for genomic sequence storage, lossless compression, and basic analysis. Built with FastAPI (backend) and React + Vite (frontend).

## Repository Structure

```
GENOVISTA/
├─ backend/
│  └─ data/               # DNA files (*.txt) and compressed (*.gz)
└─ frontend/
```


## Prerequisites

- Python 3.9+
- Node.js 18+

## Backend Setup (FastAPI)

- Path: `backend/`
- Virtualenv (example):
```powershell
# Windows PowerShell
python -m venv venv
./venv/Scripts/Activate.ps1
pip install fastapi uvicorn
```
- CORS is enabled in `backend/app/main.py` for `http://localhost:5173`.
- Run:
```powershell
# From backend/
python -m uvicorn app.main:app --reload --port 8000
```
- Docs: `http://localhost:8000/docs`
- Data path: `backend/data/`
  - New uploads: `data/{id}.txt`
  - Legacy support: `data/{id}_*.txt` still recognized by list/get.

## Frontend Setup (React + Vite)

- Path: `frontend/`
- Configure API base (optional):
```powershell
copy .env.example .env
# Edit VITE_API_BASE if backend URL differs (default http://localhost:8000)
```
- Install and run:
```powershell
npm install
npm run dev
```
- URL: `http://localhost:5173`

## Core UI Flows

- **Left panel**
  - `Upload Sequence`: Create new DNA (form clears on success; nothing auto-selected).
  - `Sequences` list: Preview, length, `.gz` tag, per-item `Edit` and `Delete`.
- **Right panel**
  - When selecting a DNA: Shows the full DNA (wraps on mobile) and action cards: Compress, Decompress, GC, Frequency, Motif.
  - When editing: The form title changes to `Update Sequence` with Cancel and Update actions.

## API Reference

Base URL: `${VITE_API_BASE}` (frontend) / `http://localhost:8000` by default.

- **Health/Root**
  - `GET /` → `{ message }`

- **List/Upload**
  - `GET /sequences/` → `{ items: [{ id, preview, length, compressed }] }`
  - `POST /sequences/` body: `{ sequence: string }` → `{ id, length, message }`

- **Read/Update/Delete**
  - `GET /sequences/{id}` → `{ id, sequence, length }`
  - `PUT /sequences/{id}` body: `{ sequence }` → `{ id, length, message }`
  - `DELETE /sequences/{id}` → `{ id, message }`

- **Compression**
  - `POST /sequences/{id}/compress` → `{ id, original_size_bytes, compressed_size_bytes, compression_ratio, compressed_file, message }`
  - `GET /sequences/{id}/decompress` → `{ id, sequence_preview, length, lossless_verification, message }`

- **Analysis**
  - `GET /sequences/{id}/gc` → `{ id, length, G_count, C_count, GC_percent, message }`
  - `GET /sequences/{id}/freq` → `{ id, length, counts, percentages, message }`

- **Motif**
  - `POST /sequences/{id}/motif` body: `{ pattern: string, use_regex: boolean }` → `{ id, pattern, use_regex, total_matches, matches }`

## Important Behaviors

- **Validation**: Upload/Update accept only A/T/C/G (case-insensitive; normalized to uppercase). Empty is rejected.
- **File Layout**: `id.txt` holds the raw DNA; compression writes `id.txt.gz`.
- **Update**: Replaces DNA, removes existing `.gz` for that ID to avoid stale compressed content.
- **Delete**: Removes `.txt` and any `.gz` for the ID.
- **Legacy Compatibility**: `list` and `get` support `id_*.txt` created by older versions.

## CORS

`backend/app/main.py` configures CORS via `CORSMiddleware` for:
- `http://localhost:5173`
- `http://127.0.0.1:5173`

If the frontend origins differ, update the `allow_origins` list.

## Development Notes

- **Run concurrently**:
  - Terminal A (backend): `uvicorn app.main:app --reload --port 8000`
  - Terminal B (frontend): `npm run dev`
- **Styling**: `frontend/src/styles.css` provides minimal, responsive UI. Layout switches to single column on <=768px.
- **Environment**: Set `VITE_API_BASE` in `frontend/.env`.


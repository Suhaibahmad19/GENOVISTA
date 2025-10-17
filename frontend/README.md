# GENOVISTA Frontend

A minimal, user-friendly React app for the GENOVISTA FastAPI backend.

## Features

- **Upload DNA sequence** to `/sequences/`
- **Compress** sequence `/sequences/{id}/compress`
- **Decompress & verify** `/sequences/{id}/decompress`
- **GC content** `/sequences/{id}/gc`
- **Nucleotide frequency** `/sequences/{id}/freq`
- **Motif search** `/sequences/{id}/motif`

## Prerequisites

- Node.js 18+
- Running backend at `VITE_API_BASE` (default `http://localhost:8000`)

## Setup

```bash
# from GENOVISTA/frontend
cp .env.example .env   # set VITE_API_BASE if needed
npm install
npm run dev
```

Open http://localhost:5173

## Build

```bash
npm run build
npm run preview
```

## Configure API base

Set `VITE_API_BASE` in `.env` to your FastAPI URL, e.g. `http://127.0.0.1:8000`.


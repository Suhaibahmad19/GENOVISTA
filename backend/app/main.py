from fastapi import FastAPI
from app.routers import sequences
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="GENOVISTA Backend",
    description="Backend for Genomic Compression & Analysis Platform",
    version="0.1"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# register router
app.include_router(sequences.router, prefix="/sequences", tags=["Sequences"])

@app.get("/")
def root():
    return {"message": "Welcome to GENOVISTA Backend API!"}

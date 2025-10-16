from fastapi import FastAPI
from app.routers import sequences

app = FastAPI(
    title="GENOVISTA Backend",
    description="Backend for Genomic Compression & Analysis Platform",
    version="0.1"
)

# register router
app.include_router(sequences.router, prefix="/sequences", tags=["Sequences"])

@app.get("/")
def root():
    return {"message": "Welcome to GENOVISTA Backend API!"}

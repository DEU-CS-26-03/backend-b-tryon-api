from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys

app = FastAPI(title="Capstone Virtual Try-On API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "success", 
        "python": sys.version,
        "uvicorn": "running",
        "service": "vton-ai"
    }

@app.get("/ready")
def ready():
    return {"message": "Capstone infrastructure ready for IDM-VTON integration!"}

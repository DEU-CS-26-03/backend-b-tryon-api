# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import RESULTS_DIR
from app.routers import jobs_router
# from app.routers import tryon_router  # tryon_router 구현 후 주석 해제

app = FastAPI(title="Capstone Python AI Server")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")

app.include_router(jobs_router.router)
# app.include_router(tryon_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Capstone Python AI Server"}
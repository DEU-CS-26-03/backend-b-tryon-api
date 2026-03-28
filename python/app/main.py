# python/app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import RESULTS_DIR
from .routers import tryon_router
from . import jobs_router

app = FastAPI()

# 결과 이미지 URL: /results/{job_id}/output.png
app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")
app.include_router(tryon_router.router)
app.include_router(jobs_router.router)
# /tryon 엔드포인트 등록
@app.get("/health")
async def health():
    return {"status": "ok"}

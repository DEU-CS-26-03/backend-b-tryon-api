from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from app.services.tryon_service import TryonService
from app.routers.tryon_router import router as tryon_router
from app.routers.jobs_router import router as jobs_router

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:8080"
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[startup] CatVTON 파이프라인 로딩 중...")
    TryonService.get_instance()
    print("[startup] 로딩 완료")
    yield


app = FastAPI(title="Capstone VirtualTryon API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})


app.include_router(tryon_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
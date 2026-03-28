# demo.ver 

import os
import uuid
import shutil
import subprocess
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="Capstone Try-On API")

TRYON_MODE = os.getenv("TRYON_MODE", "mock").lower()
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "/app/workspace"))
MOCK_RESULT_IMAGE = Path(os.getenv("MOCK_RESULT_IMAGE", "/app/workspace/mock/mock_result.jpg"))
IDM_VTON_ROOT = Path(os.getenv("IDM_VTON_ROOT", "/app/vton"))

INPUT_DIR = WORKSPACE_DIR / "input"
OUTPUT_DIR = WORKSPACE_DIR / "output"
TEMP_DIR = WORKSPACE_DIR / "temp"

for directory in [INPUT_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def validate_image(upload_file: UploadFile):
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="파일명이 비어 있습니다.")
    if not upload_file.content_type or not upload_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")


def save_upload_file(upload_file: UploadFile, destination: Path):
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)


def run_mock_tryon(result_path: Path):
    if not MOCK_RESULT_IMAGE.exists():
        raise HTTPException(status_code=500, detail="mock 결과 이미지가 없습니다.")
    shutil.copy(MOCK_RESULT_IMAGE, result_path)


def run_real_tryon(person_path: Path, garment_path: Path, result_path: Path):
    if not IDM_VTON_ROOT.exists():
        raise HTTPException(status_code=500, detail="IDM-VTON 경로가 없습니다.")

    # 실제 IDM-VTON 연결 전 임시 예시
    # 여기서는 real 모드 골격만 잡고, 나중에 inference.py 호출 로직으로 교체
    cmd = [
        "python",
        str(IDM_VTON_ROOT / "inference.py"),
        "--output_dir",
        str(OUTPUT_DIR),
    ]

    try:
        subprocess.run(cmd, check=True, cwd=str(IDM_VTON_ROOT))
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"IDM-VTON 실행 실패: {str(e)}")

    if not result_path.exists():
        raise HTTPException(status_code=500, detail="real try-on 결과 파일이 생성되지 않았습니다.")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": TRYON_MODE,
        "workspace": str(WORKSPACE_DIR)
    }


@app.post("/tryon")
async def tryon(
    person: UploadFile = File(...),
    garment: UploadFile = File(...)
):
    validate_image(person)
    validate_image(garment)

    job_id = str(uuid.uuid4())
    person_ext = Path(person.filename).suffix or ".jpg"
    garment_ext = Path(garment.filename).suffix or ".jpg"

    person_path = INPUT_DIR / f"{job_id}_person{person_ext}"
    garment_path = INPUT_DIR / f"{job_id}_garment{garment_ext}"
    result_path = OUTPUT_DIR / f"{job_id}_result.jpg"

    try:
        save_upload_file(person, person_path)
        save_upload_file(garment, garment_path)

        if TRYON_MODE == "mock":
            run_mock_tryon(result_path)
        elif TRYON_MODE == "real":
            run_real_tryon(person_path, garment_path, result_path)
        else:
            raise HTTPException(status_code=500, detail="TRYON_MODE 설정이 잘못되었습니다.")

        if not result_path.exists():
            raise HTTPException(status_code=500, detail="결과 이미지 생성 실패")

        return FileResponse(
            path=result_path,
            media_type="image/jpeg",
            filename=f"{job_id}_result.jpg"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.get("/tryon/{file_name}")
def get_tryon_result(file_name: str):
    target = OUTPUT_DIR / file_name
    if not target.exists():
        raise HTTPException(status_code=404, detail="결과 파일을 찾을 수 없습니다.")
    return FileResponse(path=target, media_type="image/jpeg", filename=file_name)


@app.get("/")
def root():
    return JSONResponse({
        "message": "Capstone Python AI Server",
        "tryon_mode": TRYON_MODE
    })


app = FastAPI()
app.include_router(router)
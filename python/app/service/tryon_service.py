# python/app/service/tryon_service.py

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import UploadFile

from vton.vton import run_tryon_pipeline

BASE_DIR = Path(__file__).resolve().parents[2]
WORKSPACE = BASE_DIR / "workspace"
INPUT_DIR = WORKSPACE / "input"

INPUT_DIR.mkdir(parents=True, exist_ok=True)


def _save_upload_to_workspace(upload: UploadFile, prefix: str) -> str:
    suffix = Path(upload.filename).suffix or ".jpg"
    tmp = NamedTemporaryFile(delete=False, dir=INPUT_DIR, prefix=prefix + "_", suffix=suffix)
    content = upload.file.read()
    tmp.write(content)
    tmp.close()
    return tmp.name


async def run_tryon(user: UploadFile, cloth: UploadFile) -> str:
    """
    FastAPI 라우터에서 직접 호출하는 동기/비동기 서비스 함수.
    Celery 없이도 먼저 동작 확인용.
    """
    user_path = _save_upload_to_workspace(user, "user")
    cloth_path = _save_upload_to_workspace(cloth, "cloth")

    result_path = await run_tryon_pipeline(user_path, cloth_path)
    return result_path

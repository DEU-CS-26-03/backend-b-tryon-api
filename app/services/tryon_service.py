# app/services/tryon_service.py
import asyncio
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import BackgroundTasks, UploadFile

from app.core.config import UPLOADS_DIR
from app.schemas.tryon_schemas import TryonRequest

# vton/scripts/vton.py 에 run_tryon_pipeline 이 정의되어 있다고 가정
from vton.scripts.vton import run_tryon_pipeline

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _save_bytes_to_workspace(data: bytes, prefix: str, suffix: str = ".jpg") -> str:
    tmp = NamedTemporaryFile(
        delete=False, dir=UPLOADS_DIR, prefix=prefix + "_", suffix=suffix
    )
    tmp.write(data)
    tmp.close()
    return tmp.name


def _schedule_delete(background: BackgroundTasks, path: str) -> None:
    path_obj = Path(path)

    def _delete():
        try:
            if path_obj.exists():
                path_obj.unlink()
        except Exception:
            pass

    background.add_task(_delete)


async def run_tryon_upload(
    user: UploadFile,
    cloth: UploadFile,
    background: BackgroundTasks,
) -> str:
    """FastAPI 라우터용 비동기 버전."""
    user_bytes  = await user.read()
    cloth_bytes = await cloth.read()

    user_path  = _save_bytes_to_workspace(user_bytes,  "user",  Path(user.filename).suffix)
    cloth_path = _save_bytes_to_workspace(cloth_bytes, "cloth", Path(cloth.filename).suffix)

    _schedule_delete(background, user_path)
    _schedule_delete(background, cloth_path)

    return await run_tryon_pipeline(user_path, cloth_path)


def run_tryon_paths(user_path: str, cloth_path: str) -> str:
    """동기 테스트 전용 (UploadFile 없이 경로만 받음)."""
    return asyncio.run(run_tryon_pipeline(user_path, cloth_path))


async def run_tryon_service(req: TryonRequest) -> dict:
    """스키마 객체를 받아 파이프라인 호출."""
    result_path = await run_tryon_pipeline(req.human_local_path, req.cloth_local_path)
    return {"result_path": result_path}
# python/app/service/tryon_service.py

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import UploadFile, BackgroundTasks

from vton.vton import run_tryon_pipeline  # async 함수라고 가정
from ...vton.vton import run_tryon_pipeline
from ..schemas import TryonRequest

BASE_DIR = Path(__file__).resolve().parents[2]
WORKSPACE = BASE_DIR / "workspace"
INPUT_DIR = WORKSPACE / "input"

INPUT_DIR.mkdir(parents=True, exist_ok=True)


def _save_bytes_to_workspace(data: bytes, prefix: str, suffix: str = ".jpg") -> str:
    tmp = NamedTemporaryFile(
        delete=False, dir=INPUT_DIR, prefix=prefix + "_", suffix=suffix
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
            # 로그만 남기고 무시해도 됨
            pass

    background.add_task(_delete)


async def run_tryon_upload(
    user: UploadFile,
    cloth: UploadFile,
    background: BackgroundTasks,
) -> str:
    """
    FastAPI 라우터에서 쓰는 비동기 버전.
    UploadFile -> 임시 파일 저장 -> async 파이프라인 호출.
    """
    user_bytes = await user.read()
    cloth_bytes = await cloth.read()

    user_path = _save_bytes_to_workspace(user_bytes, "user", Path(user.filename).suffix)
    cloth_path = _save_bytes_to_workspace(cloth_bytes, "cloth", Path(cloth.filename).suffix)

    _schedule_delete(background, user_path)
    _schedule_delete(background, cloth_path)

    result_path = await run_tryon_pipeline(user_path, cloth_path)
    return result_path


def run_tryon_paths(user_path: str, cloth_path: str) -> str:
    """
    tests/test_vton_local.py에서 사용하는 동기 버전.
    UploadFile에 의존하지 않고 순수 파일 경로만 받는다.
    """
    # run_tryon_pipeline 이 async 이라면 asyncio.run 으로 감싸기
    import asyncio

    return asyncio.run(run_tryon_pipeline(user_path, cloth_path))

def run_tryon_service(req: TryonRequest) -> dict:
    return run_tryon_pipeline(req)
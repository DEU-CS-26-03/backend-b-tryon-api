# python/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ── 모델 경로 ──────────────────────────────────────
    BASE_MODEL_PATH: str = "/app/models/catvton/stable-diffusion-inpainting"
    RESUME_PATH: str     = "/app/models/catvton/mix"

    # ── 작업 디렉토리 (컨테이너 내부) ──────────────────
    RESULTS_DIR: str     = "/app/workspace/results"
    UPLOAD_DIR: str      = "/app/workspace/uploads"

    # ── Spring 서버 정보 ────────────────────────────────
    # 추론 완료 후 이미지를 Spring으로 전송할 API 엔드포인트
    SPRING_UPLOAD_URL: str   = "http://217.142.255.158:8080/api/results/upload"
    # Spring이 이미지를 서빙하는 공개 URL (프론트/DB 저장용)
    RESULT_BASE_URL: str     = "http://217.142.255.158:8080/results"

    # ── 실행 모드 ──────────────────────────────────────
    TRYON_MODE: str      = "mock"
    APP_ENV: str         = "local"

    class Config:
        env_file = ".env"

settings = Settings()
# python/app/schemas.py

from pydantic import BaseModel


class TryonRequest(BaseModel):
    human_local_path: str | None = None
    cloth_local_path: str | None = None
    lora_strength: float | None = 1.0  # 0.0~1.0 사이로 사용


class TryonResponse(BaseModel):
    job_id: str
    mode: str
    result_url: str

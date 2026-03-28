# python/vton/external_vton_api.py

import os
from pathlib import Path
from typing import Tuple

import httpx
from fastapi import HTTPException, status


VTON_API_URL = os.getenv("VTON_API_URL", "")  # 필수 값이면 기본값 없이 두는 것도 가능
VTON_API_KEY = os.getenv("VTON_API_KEY")      # .env나 환경변수에서 주입


async def call_external_vton_api(
    user_image_path: str,
    cloth_image_path: str,
) -> Tuple[bytes, str]:
    if not VTON_API_URL or not VTON_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="VTON API env variables not configured",
        )

    user_path = Path(user_image_path)
    cloth_path = Path(cloth_image_path)

    headers = {
        "Authorization": f"Bearer {VTON_API_KEY}",
    }

    files = {
        "user_image": (user_path.name, user_path.read_bytes(), "image/png"),
        "cloth_image": (cloth_path.name, cloth_path.read_bytes(), "image/png"),
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(VTON_API_URL, headers=headers, files=files)
            resp.raise_for_status()
    except httpx.HTTPError as e:
        # 외부 API 문제를 502로 래핑
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"VTON API request failed: {e}",
        )

    content_type = resp.headers.get("Content-Type", "image/png")
    return resp.content, content_type

# python/vton/external_vton_api.py

from pathlib import Path
from typing import Tuple
import httpx  # 비동기 HTTP 클라이언트

# 실제 사용하는 외부 VTON API 정보로 바꿔야 함 [web:56][web:97][web:100]
VTON_API_URL = "https://api.example.com/v1/tryon"
VTON_API_KEY = "YOUR_API_KEY_HERE"  # .env나 config로 빼는 게 좋음


async def call_external_vton_api(
    user_image_path: str,
    cloth_image_path: str,
) -> Tuple[bytes, str]:
    """
    외부 VTON API를 호출해서 결과 이미지를 받아온다.
    반환값: (이미지 바이너리, content_type)
    """
    user_path = Path(user_image_path)
    cloth_path = Path(cloth_image_path)

    headers = {
        "Authorization": f"Bearer {VTON_API_KEY}",
    }

    files = {
        "user_image": (user_path.name, user_path.read_bytes(), "image/jpeg"),
        "cloth_image": (cloth_path.name, cloth_path.read_bytes(), "image/jpeg"),
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(VTON_API_URL, headers=headers, files=files)
        resp.raise_for_status()

    # API가 바로 이미지 바이너리를 돌려준다고 가정
    content_type = resp.headers.get("Content-Type", "image/png")
    return resp.content, content_type

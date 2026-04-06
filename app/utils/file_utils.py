# app/utils/file_utils.py
# demo.ver에서 유틸 추출

import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile


def validate_image(upload_file: UploadFile) -> None:
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="파일명이 비어 있습니다.")
    if not upload_file.content_type or not upload_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")


def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
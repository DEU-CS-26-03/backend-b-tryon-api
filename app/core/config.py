# app/core/config.py

import os
from enum import Enum
from pathlib import Path


class TryonMode(str, Enum):
    MOCK = "mock"
    REAL = "real"


TRYON_MODE: TryonMode = TryonMode(os.getenv("TRYON_MODE", "mock"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# app/core/config.py 기준: parents[0]=core, parents[1]=app, parents[2]=프로젝트루트
BASE_DIR = Path(__file__).resolve().parents[2]

WORKSPACE_DIR = BASE_DIR / "workspace"
RESULTS_DIR   = WORKSPACE_DIR / "results"
UPLOADS_DIR   = WORKSPACE_DIR / "uploads"   # 기존 workspace/input → uploads로 변경
TEMP_DIR      = WORKSPACE_DIR / "temp"
MOCK_DIR      = WORKSPACE_DIR / "mock"

# ComfyUI 경로: vton/comfyui/ 하위로 통일
WORKFLOW_JSON_PATH = os.getenv(
    "WORKFLOW_JSON_PATH",
    str(BASE_DIR / "vton" / "comfyui" / "input" / "catvton_workflow.json"),
)
COMFY_OUTPUT_PATH = os.getenv(
    "COMFY_OUTPUT_PATH",
    str(BASE_DIR / "vton" / "comfyui" / "output" / "catvton_output.png"),
)

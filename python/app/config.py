# python/app/config.py

import os
from enum import Enum
from pathlib import Path


class TryonMode(str, Enum):
    MOCK = "mock"
    REAL = "real"


TRYON_MODE: TryonMode = TryonMode(os.getenv("TRYON_MODE", "mock"))

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

BASE_DIR = Path(__file__).resolve().parents[2]
RESULTS_DIR = BASE_DIR / "DATA_DIR" / "results"

# ComfyUI 관련 (경로는 네 환경에 맞게 수정)
WORKFLOW_JSON_PATH = os.getenv(
    "WORKFLOW_JSON_PATH",
    str(BASE_DIR / "workspace" / "input" / "catvton_workflow.json"),
)

COMFY_OUTPUT_PATH = os.getenv(
    "COMFY_OUTPUT_PATH",
    str(BASE_DIR / "workspace" / "output" / "catvton_output.png"),
)

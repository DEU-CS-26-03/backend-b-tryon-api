# python/vton/comfy_client.py

import json
from pathlib import Path
from urllib import request
from shutil import copy2
from time import sleep

SERVER_URL = "http://127.0.0.1:8188"


def send_catvton_prompt(workflow_json_path: str) -> None:
    workflow_path = Path(workflow_json_path)
    prompt = json.loads(workflow_path.read_text(encoding="utf-8"))

    payload = {"prompt": prompt}
    data = json.dumps(payload).encode("utf-8")

    req = request.Request(f"{SERVER_URL}/prompt", data=data)
    request.urlopen(req)


def run_catvton_and_copy(
    workflow_json_path: str,
    comfy_output_path: str,
    save_path: str,
    wait_sec: float = 3.0,
) -> None:
    send_catvton_prompt(workflow_json_path)
    sleep(wait_sec)
    src = Path(comfy_output_path)
    copy2(src, save_path)

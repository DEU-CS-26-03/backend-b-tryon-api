FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/vton/catvton" \
    HF_HOME=/app/models/hf-cache \
    HUGGINGFACE_HUB_CACHE=/app/models/hf-cache \
    TORCH_HOME=/app/models/torch-cache \
    TZ=Asia/Seoul

WORKDIR /app

# 시스템 라이브러리 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    git wget curl libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# 1단계: CatVTON 기본 의존성 설치
COPY python/vton/catvton/requirements.txt /tmp/catvton-requirements.txt
RUN grep -vE '^(torch|torchvision|torchaudio|diffusers)(==|>=|<=|~=|!=|$)' \
        /tmp/catvton-requirements.txt \
        > /tmp/catvton-requirements-no-torch.txt \
    && python -m pip install --no-cache-dir -r /tmp/catvton-requirements-no-torch.txt || true

# 2단계: 소스 코드 복사
COPY python/ ./

# 3단계: ★ 에러 해결을 위한 패키지 버전 강제 설치 (중요)
RUN python -m pip install --no-cache-dir \
    diffusers==0.27.2 \
    transformers==4.39.3 \
    accelerate==0.28.0 \
    huggingface_hub==0.25.2 \
    peft==0.12.0 \
    numpy==1.26.4 \
    pillow==10.3.0 \
    tqdm yacs PyYAML omegaconf

RUN mkdir -p \
    /app/workspace/uploads \
    /app/workspace/results \
    /app/workspace/temp \
    /app/models/hf-cache \
    /app/models/torch-cache

EXPOSE 8000

CMD ["uvicorn", "app.app_api:app", "--host", "0.0.0.0", "--port", "8000"]
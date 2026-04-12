FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

COPY vton/CatVTON/requirements.txt /tmp/catvton-requirements.txt
RUN grep -vE '^(torch|torchvision|torchaudio)(==|>=|<=|$)' /tmp/catvton-requirements.txt > /tmp/catvton-requirements-no-torch.txt && \
    python -m pip install --no-cache-dir -r /tmp/catvton-requirements-no-torch.txt || true

RUN python -m pip install --no-cache-dir \
    torch==2.7.1 \
    torchvision==0.22.1 \
    torchaudio==2.7.1 \
    --index-url https://download.pytorch.org/whl/cu128

RUN python -m pip install --no-cache-dir \
    diffusers==0.38.0.dev0 \
    transformers==4.53.1 \
    accelerate==0.34.2 \
    huggingface_hub==0.36.2 \
    peft \
    numpy \
    pillow

COPY app/ /app/app/
COPY vton/ /app/vton/

RUN mkdir -p \
    /app/workspace/uploads \
    /app/workspace/results \
    /app/workspace/temp \
    /app/models/hf-cache \
    /app/models/torch-cache

ENV HF_HOME=/app/models/hf-cache
ENV HUGGINGFACE_HUB_CACHE=/app/models/hf-cache
ENV TORCH_HOME=/app/models/torch-cache
ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["sleep", "infinity"]
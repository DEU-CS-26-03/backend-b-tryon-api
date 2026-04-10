FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY vton/CatVTON/requirements.txt /tmp/catvton-requirements.txt
RUN grep -vE '^(torch|torchvision|torchaudio)(==|>=|<=|$)' /tmp/catvton-requirements.txt > /tmp/catvton-requirements-no-torch.txt
RUN pip install --no-cache-dir -r /tmp/catvton-requirements-no-torch.txt

RUN pip install --no-cache-dir \
    torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 \
    --index-url https://download.pytorch.org/whl/cu128

RUN pip install --no-cache-dir accelerate==0.32.1
RUN pip install --no-cache-dir "transformers>=4.53.1"

COPY app/ ./app/
COPY vton/ ./vton/

RUN mkdir -p /app/workspace/uploads \
             /app/workspace/results \
             /app/workspace/temp \
             /app/models/hf-cache

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 선택적 복사 (workspace는 볼륨 마운트로 처리)
COPY app/ ./app/
COPY vton/ ./vton/

# workspace 빈 디렉토리 생성 (볼륨 마운트 전 fallback)
RUN mkdir -p workspace/uploads workspace/results workspace/temp

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
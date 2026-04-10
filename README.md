# CatVTON 모델 추론

---
다음 명령어로 CatVTON 설치해서 환경 맞추시면 됩니다.
git clone https://github.com/Zheng-Chong/CatVTON.git .\vton\CatVTON

본 셋팅은 rtx5060 기준이기 때문에 본인 셋팅 확인하시고 docker 파일들 변경하세요

FROM python:3.11-slim -> FROM python:3.10-slim 호환성 때문에 수정할것 같습니다.


requeast하려면 다음과 같은 항목을 중점으로 체크하세요.
1. compose-ai.yml
2. Dockerfile
3. .env(.env.example)
4. vton/CatVTON/run_one.py

vton 안에서는 학습이 이루어지는 디렉토리입니다. 디렉토리 안에서 모델 업그레이드가 이루어지는 걸 권장합니다.
workspace는 모델의 추론이 일어나는 준비물/결과물 폴더 입니다. results에서 도출되면 확인하면 됩니다.


# CatVTON 테스트 기록

## 1. 목적
우리 프로젝트에서 가상 피팅 모델로 CatVTON을 적용할 수 있는지 확인하기 위해 로컬 Docker 환경에서 1회성 추론 테스트를 진행했다.

이번 테스트의 목표는 다음과 같다.
- Docker 기반으로 CatVTON 실행 가능 여부 확인
- `workspace/uploads`의 입력 이미지 2장을 사용해 결과 이미지를 생성할 수 있는지 확인
- 생성 결과를 `workspace/results`에 저장하는 흐름 검증
- 추후 Spring API와 연동 가능한 구조로 확장 가능한지 판단

## 2. 참고한 공식 정보
CatVTON 공식 저장소는 가상 피팅 diffusion 모델이며, 공식 설치 예시는 Python 3.9 기반 conda 환경에서 `pip install -r requirements.txt`를 수행하는 방식으로 안내되어 있다.  
또한 공식 requirements 예시에는 `torch==2.4.0`, `torchvision==0.19.0`, `accelerate==0.31.0`, `numpy==1.26.4` 등이 포함되어 있고, 공식 추론 코드는 체크포인트를 Hugging Face에서 자동 다운로드하는 구조다.

## 3. 우리 프로젝트 적용 방식
공식 문서는 conda 환경 기준이지만, 우리 프로젝트는 백엔드 구조상 Docker 중심으로 운영하기 위해 별도 가상환경 대신 Docker 컨테이너 안에서 CatVTON을 실행하는 방향으로 테스트했다.

프로젝트 디렉토리에서 주요 테스트 경로는 아래와 같다.

- `vton/CatVTON`: CatVTON 코드 위치
- `workspace/uploads`: 입력 이미지 저장 위치
- `workspace/results`: 생성 결과 저장 위치
- `models`: Hugging Face / Torch 캐시 저장 위치

## 4. Docker 구성
Compose 서비스는 `catvton` 단일 서비스로 두고, 컨테이너 내부 작업 디렉토리는 `/app/vton/CatVTON`으로 설정했다.

볼륨 마운트는 다음과 같이 잡았다.
- `./vton/CatVTON -> /app/vton/CatVTON`
- `./workspace -> /app/workspace`
- `./models -> /app/models`

이렇게 구성해서 로컬에 저장된 입력 이미지와 생성 결과를 컨테이너 밖에서도 바로 확인할 수 있게 했다.

## 5. 테스트 과정
처음에는 공식 버전에 가깝게 맞춘 환경으로 실행을 시도했다.

하지만 실제 테스트 과정에서 다음과 같은 의존성 충돌이 발생했다.
- `huggingface_hub` 관련 import 오류
- `accelerate` 관련 import 오류
- `diffusers`와 `transformers` 버전 불일치 오류

그래서 현재 테스트에서는 실제 컨테이너 안에 설치된 패키지 조합을 기준으로 버전을 다시 맞추는 방식으로 조정했다.

추가로 로컬 테스트 장비가 RTX 5060 Laptop GPU였기 때문에, 현재 설치된 PyTorch가 `sm_120`을 완전히 지원하지 않는 경고가 있었다.
따라서 이번 로컬 결과는 “최종 성능 검증”보다는 “입출력 흐름 검증”과 “기본 실행 가능성 확인”에 더 의미를 둔다.

## 6. 실행 방식
Gradio UI 실행 대신, 입력 이미지 2장을 바로 읽어서 결과 1장을 저장하는 1회성 테스트 스크립트를 사용했다.

예시 실행 방식:

```bash
python /app/vton/CatVTON/run_one.py \
  --person /app/workspace/uploads/person.jpg \
  --cloth /app/workspace/uploads/cloth.jpg \
  --cloth_type upper \
  --output /app/workspace/results/catvton-once \
  --mixed_precision bf16 \
  --allow_tf32
```

입력값:
- 사람 이미지 1장
- 의류 이미지 1장
- `cloth_type`으로 상의/하의/전체 의상 구분

출력값:
- `/app/workspace/results/catvton-once` 경로에 결과 이미지 저장

## 7. 테스트 결과
현재 기준으로는 Docker 환경에서 CatVTON을 실행하고, 입력 이미지 2장을 기반으로 결과 이미지를 생성하는 흐름까지 확인했다.

특히 아래 항목을 검증했다.
- Docker 컨테이너 실행 가능
- GPU 인식 여부 확인
- Hugging Face 체크포인트 다운로드 가능
- 입력 이미지 경로 연결 가능
- 결과 이미지 파일 저장 가능

즉, “웹서비스에서 업로드된 이미지 2장을 받아 결과 이미지를 생성하고 반환하는 최소 기능”은 구현 가능한 상태라고 판단했다.

## 8. 한계 및 관찰 내용
테스트 결과상 상의/하의 구분이 애매한 경우가 있었고, 질감 표현도 입력 이미지 품질에 따라 차이가 있었다.

따라서 다음 항목이 추가 검증 포인트다.
- `cloth_type=upper / lower / overall` 별 품질 비교
- 질감이 강한 의류(니트, 데님, 체크, 줄무늬)에 대한 보존력 확인
- 동일 인물 기준 상의/하의 별도 테스트
- 실제 운영 GPU(예상 3070 Ti) 환경에서 재검증

## 9. 향후 계획
운영 구조는 다음처럼 분리하는 방향이 적절하다.

- Spring 서버: 사용자 요청 수신, 인증, 작업 상태 관리
- Python 추론 서버: CatVTON 실행 전용 API
- 스토리지: 입력/결과 이미지 저장

즉, 웹사이트는 결과 이미지만 보여주고, 실제 추론은 별도 Python 서비스가 담당하도록 구성하는 방향으로 진행할 예정이다.
<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

 **핵심은 “셋업은 한 번에, 역할은 분리해서”** 가는 거다.[query] 저희의 프로젝트는 Docker Compose 기반으로 Spring, Python, MySQL, Redis가 함께 뜨는 구조라서, 팀원별 실행 방법과 담당 범위 md파일로 분명히 적어 온보딩 하게 되었습니다.[query][^1]


# Capstone Virtual Fitting Project

3인 팀 캡스톤 프로젝트입니다.  
Docker Compose 기반으로 Spring Boot, FastAPI, MySQL, Redis를 함께 실행합니다.  
현재는 **mock 모드 기준으로 가상 피팅 API 연동 테스트가 가능**한 상태입니다.

## 기술 스택

- Spring Boot 3.3.2 [백엔드 API]
- FastAPI + Python 3.11 [가상 피팅 AI API]
- MySQL 8.0 [DB]
- Redis 7 [캐시 / 작업 상태 관리 예정]
- Docker Compose [공통 개발 환경]

## 팀 역할

- 팀원 A: Spring Boot 백엔드 API, DB 연동, Python 서버 호출
- 팀원 B: Python FastAPI, mock/real try-on API, IDM-VTON 연동
- 팀원 C: 프론트엔드(UI), 이미지 업로드/결과 화면, API 연결

## 프로젝트 실행 전 준비

아래 프로그램이 설치되어 있어야 합니다.

- Docker Desktop [필수]
- Git [필수]
- Java 17 [Spring 로컬 실행 시 선택]
- Python 3.11 [Python 로컬 실행 시 선택]

Docker Desktop에는 Docker Compose가 포함되어 있습니다.[web:340][web:339]

## 프로젝트 실행 방법

### 1. 프로젝트 받기

```bash
git clone <repo-url>
cd Project_docker_test
```


### 2. 환경변수 파일 생성

`.env.example` 파일을 복사해서 `.env` 파일을 만듭니다.[web:342]

```bash
cp .env.example .env
```

Windows PowerShell에서는 아래처럼 직접 만들어도 됩니다.

```powershell
Copy-Item .env.example .env
```


### 3. mock 결과 이미지 확인

아래 파일이 있어야 합니다.

```bash
python/mock/mock_result.jpg
```


### 4. Spring jar 빌드

Spring 컨테이너는 `build/libs/*.jar`를 복사해서 실행하므로, 먼저 jar 빌드가 필요합니다.[web:320][web:352]

```powershell
cd .\spring
.\gradlew.bat build
cd ..
```


### 5. 전체 서비스 실행

프로젝트 루트에서 실행합니다.[web:343]

```powershell
docker compose up --build
```


### 6. 실행 확인

```powershell
docker compose ps
```

정상 실행 시 아래 서비스가 떠야 합니다.

- capstone-mysql
- capstone-redis
- capstone-python
- capstone-spring


## 확인 가능한 주소

- Python Health Check: `http://localhost:8000/health`
- Spring API: `http://localhost:8080`
- MySQL: `localhost:3306`
- Redis: `localhost:6379`


## mock 모드 테스트

현재 Python 서버는 `TRYON_MODE=mock` 기준으로 테스트할 수 있습니다.

### Python 직접 테스트

```powershell
curl.exe -X POST "http://localhost:8000/tryon" -F "person=@person.jpg" -F "garment=@garment.jpg" --output python_result.jpg
```


### Spring 경유 테스트

```powershell
curl.exe -X POST "http://localhost:8080/api/fitting/tryon" -F "person=@person.jpg" -F "garment=@garment.jpg" --output spring_result.jpg
```


## 팀원별 작업 가이드

### 팀원 A - Spring 담당

해야 할 일:

- 상품, 사용자, 피팅 요청 API 설계
- Spring에서 Python `/tryon` 호출
- MySQL 연동
- Redis 연동 준비
- API 명세 정리

우선 작업:

- `/api/fitting/tryon` 안정화
- DB 테이블 초안 작성
- Swagger/OpenAPI 추가


### 팀원 B - Python/AI 담당

해야 할 일:

- FastAPI `/tryon` 유지보수
- mock 모드 안정화
- real 모드용 IDM-VTON 구조 설계
- 이미지 저장/결과 반환 로직 개선

우선 작업:

- `/tryon` 응답 형식 고정
- 파일 저장 경로 정리
- `TRYON_MODE=real` 분기 설계
- IDM-VTON 연동 실험


### 팀원 C - 프론트 담당

해야 할 일:

- 상품 목록 UI
- 사용자 이미지 업로드 UI
- 의상 선택 UI
- 결과 이미지 표시 화면
- Spring API 연동

우선 작업:

- 업로드 화면 먼저 구현
- Spring `/api/fitting/tryon` 연동
- 결과 이미지 미리보기 UI 구현


## 이후 진행 순서

1. mock 모드로 전체 흐름 먼저 완성
2. 프론트 ↔ Spring ↔ Python 연동 안정화
3. DB 스키마 확정
4. 피팅 요청/결과 저장 기능 추가
5. IDM-VTON real 모드 연결
6. 최종 발표용 시연 시나리오 정리

## 자주 쓰는 명령어

### 전체 실행

```powershell
docker compose up --build
```


### 백그라운드 실행

```powershell
docker compose up -d --build
```


### 종료

```powershell
docker compose down
```


### 로그 확인

```powershell
docker compose logs -f
```


### Spring만 로그 보기

```powershell
docker logs capstone-spring
```


### Python만 로그 보기

```powershell
docker logs capstone-python
```


## 주의사항

- `docker-compose.yml` 상단의 `version:` 경고는 현재 동작에는 큰 영향이 없지만, 추후 제거 예정입니다.
- PowerShell에서는 `curl` 대신 `curl.exe` 사용을 권장합니다.
- Spring은 먼저 `.\gradlew.bat build` 후 Docker 실행해야 합니다.
- mock 모드에서는 실제 AI 추론이 아니라 샘플 이미지가 반환됩니다.



## 팀원별 실행법 요약

README 본문 말고, 팀원한테 짧게 전달할 버전은 이렇게 적으면 된다.[query]

- 팀원 A: `spring` 빌드 후 `docker compose up --build`, Spring API 작업.
- 팀원 B: `python/mock/mock_result.jpg` 확인 후 Python `/tryon` 테스트, 나중에 IDM-VTON real 모드 붙이기.
- 팀원 C: Docker 전체 실행 후 Spring API만 호출해서 프론트 개발, AI 실제 연동 전까지는 mock 결과로 화면 구현.

## 이후 어떻게 진행하면 좋냐

지금부터는 기능 개발 순서를 잘 잡는 게 중요하다.

- 1주차: mock 모드 기준 전체 흐름 완성, 프론트 업로드 화면 + Spring 전달 + Python 결과 반환.
- 2주차: DB 설계, 상품/피팅 요청/결과 저장 구조 확정.
- 3주차: real 모드 분기, IDM-VTON 연동 실험.
- 4주차 이후: UX 개선, 예외 처리, 발표 시연 시나리오 정리.

## 내가 추천하는 실제 역할 분담

네가 지금 Docker/환경 셋업을 끝냈으니까, **너는 팀 리드처럼 공통 환경 유지 + Python AI 파트**, 팀원 A는 Spring API, 팀원 C는 프론트로 가는 게 가장 자연스럽다. 이 구조면 서로 병목이 적고, mock 모드 덕분에 AI가 늦어져도 전체 개발은 계속 갈 수 있다.

원하면 내가 다음 답변에서 이 README를 **너희 프로젝트 이름 기준으로 더 자연스럽게 다듬고, `.env.example` 내용까지 포함한 최종본**으로 다시 정리해줄게.
<span style="display:none">[^10][^11][^12][^13][^14][^15][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://github.com/docker/awesome-compose
[^2]: https://github.com/osteel/docker-tutorial
[^3]: https://docs.docker.com/compose/gettingstarted/index.html
[^4]: https://docs.docker.com/desktop/
[^5]: https://docs.docker.com/guides/genai-pdf-bot/containerize/
[^6]: https://github.com/brent-stone/fastapi_demo
[^7]: https://www.reddit.com/r/docker/comments/9h4hg2/how_should_i_organize_my_dockercompose_file_for_a/
[^8]: https://github.com/RajawatBanna/useful-docker-compose/blob/main/README.md
[^9]: https://velog.io/@happyjeong97/Docker-Compose-MySQL-Spring-Boot-Redis-%EB%8F%99%EC%8B%9C-%EC%8B%A4%ED%96%89
[^10]: https://last9.io/blog/docker-compose-health-checks/
[^11]: https://github.com/louiscklaw/with-docker-compose-app-windows/blob/master/README.md
[^12]: https://github.com/redis-developer/fastapi-redis-tutorial/blob/master/README.md
[^13]: https://cyberpanel.net/blog/docker-compose-healthcheck
[^14]: https://github.com/RajawatBanna/useful-docker-compose
[^15]: https://github.com/bezkoder/docker-compose-spring-boot-mysql/blob/master/README.md
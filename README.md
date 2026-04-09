## 🐬Docker 사용법

### 기본적인 docker 명령어 & hostNumber

- 실행 명령: docker compose up --build

- 종료 명령: docker compose down

- 전체 로그 보기: docker compose logs -f

- Python 확인: http://localhost:8000/health
​
- Spring 확인: http://localhost:8080

- MySQL 접속 호스트: localhost:3306

- Redis 접속 호스트: localhost:6379

## 🚀 Getting Started

1. **Clone the repository**: `git clone https://github.com/[Your-Username]/CapStone_Docker_Compose_Setting.git`
2. **Configure Environment**: Create a `.env` file in the root directory if environment variables are required for MySQL/Redis.
3. **Build and Run**: Execute `docker compose up --build` to orchestrate the Java Spring, Python, and Database containers.
4. **Verify Services**: Use the health check URLs provided above to ensure all microservices are running correctly.

### 시스템 요구사항
- Windows 11 64-bit (Pro 이상 권장): 23H2 빌드 이상.
- 64-bit CPU (SLAT 지원), 4GB RAM 이상.
- BIOS/UEFI에서 하드웨어 가상화 (Intel VT-x/AMD-V) 활성화.
- WSL 2 기능 및 Virtual Machine Platform 활성화.

### 단계별 해결
1. **BIOS 확인**: 재부팅 > BIOS (F2/Del) > Virtualization Technology Enabled > 저장.
2. **Windows 기능**: "Windows 기능 켜기/끄기" > **Virtual Machine Platform**, **Hyper-V(하이퍼바이 가상화)** 체크 > 재부팅.
3. **WSL 업데이트**: PowerShell (관리자) `wsl --update` 실행.
4. Docker 재시작 후 Task Manager > 성능 > CPU "가상화: 사용" 확인.

```
2번 Hyper-V의 주의점!

VirtualBox 등 다른 VM 소프트웨어와 Hyper-V 충돌 가능 – Docker 사용 시엔 괜찮음.
```

## *err - 1

<details>
<summary>Virtualization support not detected
Docker Desktop failed to start because virtualisation support wasn’t detected. Contact your IT admin to enable virtualization or check system requirements.</summary>
<div markdown="1">
    
    Docker Desktop에서 가상화 지원이 감지되지 않아 시작되지 않는 오류입니다. BIOS에서 가상화 기능(VT-x/AMD-V)을 활성화하고 Windows 기능을 확인하면 대부분 해결됩니다.

## **Windows 기능 활성화**

관리자 PowerShell에서 실행:

```
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
```
</div>
</details>

## *err - 2

<details>
<summary>- WSL needs updating
Your version of Windows Subsystem for Linux (WSL) is too old.
Run the command below to update or for more information, visit .the Microsoft WSL documentation
</summary>
<div markdown="1">

   **WSL 업데이트 오류는 Windows Subsystem for Linux 버전이 오래되어 발생합니다.**

## **업데이트 방법**

관리자 권한 PowerShell을 열고 다음 명령을 실행하세요.

`wsl --update`

업데이트 후 WSL을 재시작하려면 `wsl --shutdown`을 입력한 다음 Docker를 다시 시작하세요.

## **상태 확인**

WSL 상태를 확인하려면 `wsl --status` 또는 `wsl --version`을 사용하세요. 커널 버전이 최신인지 확인할 수 있습니다.

## **추가 해결책**

업데이트가 실패하면 Windows를 최신으로 업데이트하거나 `--web-download` 옵션을 추가하세요: `wsl --update --web-download`
</div>
</details>
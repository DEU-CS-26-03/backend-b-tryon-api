from pydantic import BaseModel
from typing import Optional

class TryonRequest(BaseModel):
    """
    MVP 단계에서는 이미지를 파일(Multipart)로 직접 받으므로 
    이 스키마는 주로 로컬 테스트나 추가 옵션 전달용으로 사용됩니다.
    """
    lora_strength: Optional[float] = 1.0
    # 필요한 경우 여기에 추가적인 파라미터(예: 스타일 옵션 등)를 정의합니다.


class TryonResponse(BaseModel):
    """
    스프링 서버와 프론트엔드가 결과를 확인하기 위해 사용하는 응답 스키마입니다.
    """
    job_id: str             # 작업 고유 ID
    status: str             # 작업 상태 (PROCESSING, COMPLETED, FAILED)
    mode: str               # 현재 실행 모드 (mock 또는 real)
    result_url: Optional[str] = None  # 생성된 이미지의 접근 경로
    message: Optional[str] = None     # 에러 발생 시 상세 메시지
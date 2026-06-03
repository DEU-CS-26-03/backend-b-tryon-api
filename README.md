#backend-CatVTON+ComfyUI-tryonAPI

## License & Acknowledgements

This project is for academic purposes (Capstone Design) and follows these licenses:

- **Software Core**: [ComfyUI](https://github.com/Comfy-Org/ComfyUI) (GPL-3.0 License)
- **VTON Model**: [CatVTON](https://github.com/Zheng-Chong/CatVTON) (CC BY-NC-SA 4.0 License)

### Usage Restrictions
- **Non-Commercial**: This repository is for research and educational purposes only. It **cannot** be used for commercial services or profit-making activities due to the CatVTON license.
- **Attribution**: If you use this code, please cite the original authors of ComfyUI and CatVTON.
- **ShareAlike**: Any derivative works must be distributed under the same license (CC BY-NC-SA 4.0).

### 배포 시 주의할 점 (Checklist)
Model Weights (가중치 파일): CatVTON의 모델 파일(.safetensors 등)은 용량이 크기도 하지만, 라이선스상 직접 리포지토리에 올리기보다는 다운로드 링크(HuggingFace 등)를 안내하는 방식이 관례입니다.
데이터셋: 학습에 사용한 데이터셋(VITON-HD 등)이 있다면, 해당 데이터셋의 라이선스도 '비상업적'임을 README에 짧게 언급해주는 것이 좋습니다.

#### 다음 명령어로 AI 추론 확인
```
docker logs -f capstone-python
```

##  [심사위원용] 로컬 실행 및 가중치 설정 가이드

본 프로젝트는 AI 모델(CatVTON)의 용량 최적화를 위해 가중치(Weights) 파일을 레포지토리에 포함하지 않았습니다. 원활한 코드 점검 및 실행을 위해 아래 절차를 진행해 주세요.

**1. 패키지 설치**
```bash
pip install -r requirements.txt
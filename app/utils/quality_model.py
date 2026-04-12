# app/utils/quality_model.py

from pathlib import Path
from typing import List, Tuple


class QualityModel:
    """VTON 결과 이미지 품질 점수 평가 래퍼 (추후 TF/Keras 모델로 교체 예정)."""

    def __init__(self):
        # self.model = tf.keras.models.load_model("models/quality_model.h5")
        pass

    def score_image(self, image_path: str) -> float:
        _ = Path(image_path)
        return 0.5  # TODO: 실제 모델 추론으로 교체

    def select_best(self, candidates: List[str]) -> Tuple[str, float]:
        best_path, best_score = None, -1.0
        for p in candidates:
            s = self.score_image(p)
            if s > best_score:
                best_score, best_path = s, p
        return best_path, best_score
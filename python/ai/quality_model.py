# python/ai/quality_model.py

from pathlib import Path
from typing import List, Tuple

import numpy as np

# TODO: 나중에 TensorFlow/Keras 모델 로드 코드 추가
# import tensorflow as tf


class QualityModel:
    """
    VTON 결과 이미지 품질을 점수로 평가하는 모델 래퍼.
    초기에는 더미 구현, 나중에 TensorFlow 모델로 교체 예정.
    """

    def __init__(self):
        # 예: self.model = tf.keras.models.load_model("models/quality_model.h5")
        pass

    def score_image(self, image_path: str) -> float:
        """
        단일 이미지 품질 점수를 0~1 사이로 반환.
        지금은 더미로 0.5 반환.
        """
        # TODO: 실제 구현에서는 이미지 로드 -> 전처리 -> model.predict
        _ = Path(image_path)
        return 0.5

    def select_best(self, candidates: List[str]) -> Tuple[str, float]:
        """
        여러 결과 이미지 후보 중 가장 점수가 높은 것을 선택.
        """
        best_path = None
        best_score = -1.0
        for p in candidates:
            s = self.score_image(p)
            if s > best_score:
                best_score = s
                best_path = p
        return best_path, best_score

from typing import List, Optional, Dict
from ai import feature_engineering as fe
from scipy.spatial.distance import cosine
import numpy as np
import json
import os

# :warning: 1. 임계 접근 분석
def is_threshold_approaching(current_value: float, threshold: float, delta: float, time_limit: float) -> Optional[float]:
    """
    현재 속도(delta)로 threshold 도달까지 남은 시간이 time_limit 이내인지 판단
    """
    if delta is None or delta <= 0 or current_value >= threshold:
        return None
    time_to_threshold = fe.calculate_time_to_threshold(current_value, threshold, delta)
    if time_to_threshold is not None and time_to_threshold <= time_limit:
        return time_to_threshold
    return None


# :fire: 2. 급격한 변화 감지
def is_acceleration_rising(acceleration: float, threshold: float) -> bool:
    return acceleration >= threshold


# :rotating_light: 3. 고장 패턴 유사도 분석
def is_similar_to_failure_pattern(current_vector: List[float], pattern_path: str, similarity_threshold: float = 0.85) -> Optional[float]:
    """
    현재 변화 벡터가 고장 직전 패턴과 유사한지 확인 (Cosine Similarity)
    """
    if not os.path.exists(pattern_path):
        return None

    with open(pattern_path, 'r') as f:
        patterns = json.load(f)

    max_similarity = 0.0
    for pattern in patterns:
        if len(pattern) != len(current_vector):
            continue
        similarity = 1 - cosine(current_vector, pattern)
        if similarity > max_similarity:
            max_similarity = similarity

    return max_similarity if max_similarity >= similarity_threshold else None


# :triangular_flag_on_post: 종합 판단 로직
def analyze_sensor_behavior(
    values: List[float],
    threshold: float,
    acceleration_threshold: float,
    time_limit: float,
    pattern_path: str
) -> Dict[str, Optional[float]]:
    """
    주요 판단 로직을 통합 수행
    """
    current = values[-1]
    delta = fe.calculate_average_delta(values)
    acceleration = fe.calculate_acceleration(values)
    time_to_threshold = is_threshold_approaching(current, threshold, delta, time_limit)
    acceleration_flag = is_acceleration_rising(acceleration, acceleration_threshold)
    similarity = is_similar_to_failure_pattern(values, pattern_path)

    return {
        "time_to_threshold": time_to_threshold,         # 00분 내 임계 도달 예상
        "acceleration_rising": acceleration_flag,        # 최근 변화량 급증
        "pattern_similarity": similarity                 # 과거 고장 패턴과 00% 유사
    }
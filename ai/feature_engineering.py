from typing import List, Optional

def calculate_delta(data: List[float]) -> Optional[float]:
    """마지막 두 지점의 변화량 계산"""
    if len(data) < 2:
        return None
    return data[-1] - data[-2]


def calculate_average_delta(data: List[float], window: int = 3) -> Optional[float]:
    """이전 값들과 평균 변화량 계산"""
    if len(data) < window + 1:
        return None
    diffs = [data[i+1] - data[i] for i in range(-window-1, -1)]
    return sum(diffs) / len(diffs)


def calculate_acceleration(data: List[float]) -> Optional[float]:
    """가속도 = 최근 변화량 - 이전 변화량"""
    if len(data) < 4:
        return None
    delta_now = data[-1] - data[-2]
    delta_prev = data[-2] - data[-3]
    return delta_now - delta_prev


def calculate_time_to_threshold(current: float, threshold: float, delta: Optional[float]) -> Optional[float]:
    """
    임계값까지 도달하는 데 걸리는 시간 추정 (단순 선형 모델 기반)
    - delta > 0일 때만 추정 가능
    """
    if delta is None or delta == 0:
        return None
    try:
        return (threshold - current) / delta
    except ZeroDivisionError:
        return None
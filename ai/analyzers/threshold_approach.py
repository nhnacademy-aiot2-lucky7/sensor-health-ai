from typing import Optional

class ThresholdApproachAnalyzer:
    """
    임계값 접근 분석기 - 시간 기반 예측
    현재 변화율을 기반으로 임계값 도달 시간을 예측
    """

    @staticmethod
    def analyze(current_value: float, threshold: float, delta: float, time_limit: float) -> Optional[float]:
        """
        현재 속도(delta)로 threshold 도달까지 남은 시간이 time_limit 이내인지 판단
        
        Args:
            current_value: 현재 센서 값
            threshold: 목표 임계값
            delta: 변화율 (단위 시간당 변화량)
            time_limit: 허용 가능한 최대 시간
            
        Returns:
            임계값 도달 예상 시간 (time_limit 이내일 경우), 아니면 None
        """
        # 조기 종료 조건들
        if delta is None or delta <= 0 or current_value >= threshold:
            return None

        # 임계치 분석 주기가 짧지 않기 때문에 선형으로 시간 계산
        time_to_threshold = (threshold - current_value) / delta

        # 시간 제한 내에 도달하는지 확인
        if time_to_threshold <= time_limit:
            return time_to_threshold

        return None

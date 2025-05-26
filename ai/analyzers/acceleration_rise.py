class AccelerationRiseAnalyzer:
    """
    급격한 변화 감지기 - 변화율 기반 감지
    가속도(변화율의 변화)를 통해 급격한 상승/하강을 감지
    """

    @staticmethod
    def analyze(acceleration: float, threshold: float, current_value: float, baseline: float) -> dict:
        is_rapid = abs(acceleration) >= threshold       # 급격한 변화 판단
        direction = "increasing" if acceleration > 0 else "decreasing"      # 변화 방향 판단
        severity = abs(acceleration) / threshold if threshold != 0 else 0       # 변화 심각도 계산 (ex. 임계값의 1.5배 수준)
        current_level = current_value / baseline if baseline != 0 else 0        # 현재 수준 평가 (ex. 평상시의 2.8배 수준)

        return {
            "is_rapid_change": is_rapid,
            "direction": direction,
            "severity": severity,
            "current_level": current_level
        }
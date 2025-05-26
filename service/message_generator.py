from typing import Optional, Dict


def generate_message(sensor_id: str, analysis_result: Dict[str, Optional[float]]) -> Optional[str]:
    """
    센서 ID와 이상 판단 결과를 기반으로 알림 메시지 생성
    """
    time_to_threshold = analysis_result.get("time_to_threshold")
    acceleration_rising = analysis_result.get("acceleration_rising")
    pattern_similarity = analysis_result.get("pattern_similarity")

    messages = []

    if time_to_threshold is not None:
        messages.append(
            f"⚠️ 센서 [{sensor_id}]가 약 {round(time_to_threshold, 1)}분 내 임계값에 도달할 것으로 예측됩니다."
        )

    if acceleration_rising:
        messages.append(
            f"📈 센서 [{sensor_id}]의 변화 속도가 비정상적으로 급증하고 있습니다."
        )

    if pattern_similarity is not None:
        messages.append(
            f"🛠️ 센서 [{sensor_id}]는 과거 고장 패턴과 {round(pattern_similarity * 100, 1)}% 유사합니다."
        )

    if messages:
        return "\n".join(messages)
    else:
        return None  # 이상 없음
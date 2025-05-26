from typing import List, Tuple
from model.threshold_data import ThresholdData
import numpy as np
from datetime import datetime, timedelta

class InsightAnalyzer:
    def __init__(self, threshold_time_limit_minutes: int = 60, acceleration_threshold: float = 0.5):
        """
        :param threshold_time_limit_minutes: 임계치 도달 예상 시간 제한 (분)
        :param acceleration_threshold: 변화율 급증 판단 임계값
        """
        self.threshold_time_limit = timedelta(minutes=threshold_time_limit_minutes)
        self.acceleration_threshold = acceleration_threshold

    def analyze(self, threshold_data_list: List[ThresholdData]) -> List[str]:
        """
        주어진 임계치 데이터 리스트를 분석하여 인사이트 메시지 목록 반환
        """
        insights = []

        # 1. 시간순 정렬
        sorted_data = sorted(threshold_data_list, key=lambda x: x.calculated_at)

        if len(sorted_data) < 2:
            return ["데이터 부족으로 인사이트 생성 불가"]

        # 값과 시간 리스트 추출
        times = [td.calculated_at for td in sorted_data]
        mins = np.array([td.threshold_min for td in sorted_data])
        maxs = np.array([td.threshold_max for td in sorted_data])
        avgs = np.array([td.threshold_avg for td in sorted_data])

        # 변화율 (delta) 계산 (현재값 - 이전값) / 시간 간격(초)
        time_deltas_sec = np.diff([t.timestamp() for t in times])
        if any(time_deltas_sec == 0):
            return ["중복된 timestamp 존재, 인사이트 생성 불가"]

        min_deltas = np.diff(mins) / time_deltas_sec
        max_deltas = np.diff(maxs) / time_deltas_sec
        avg_deltas = np.diff(avgs) / time_deltas_sec

        # 2. 임계 접근 분석 (예상 도달 시간 계산)
        latest = sorted_data[-1]
        def estimate_time_to_threshold(current, delta, threshold):
            if delta <= 0:
                return None
            return (threshold - current) / delta

        # 예시: threshold 임계치는 max_range_max (최대 허용값)
        t_min = estimate_time_to_threshold(latest.threshold_min, min_deltas[-1], latest.min_range_max)
        t_max = estimate_time_to_threshold(latest.threshold_max, max_deltas[-1], latest.max_range_max)
        t_avg = estimate_time_to_threshold(latest.threshold_avg, avg_deltas[-1], latest.avg_range_max)

        # 초 단위 → timedelta 변환
        def to_timedelta(seconds):
            return timedelta(seconds=seconds) if seconds is not None and seconds > 0 else None

        times_to_threshold = {
            "min": to_timedelta(t_min),
            "max": to_timedelta(t_max),
            "avg": to_timedelta(t_avg),
        }

        for key, ttt in times_to_threshold.items():
            if ttt and ttt <= self.threshold_time_limit:
                insights.append(f"⚠️ {ttt} 내 {key} 임계치 도달 예상 — 현재 변화 추세 유지 시")

        # 3. 변화율 급등 감지 (acceleration)
        min_acceleration = min_deltas[-1] - min_deltas[-2] if len(min_deltas) > 1 else 0
        max_acceleration = max_deltas[-1] - max_deltas[-2] if len(max_deltas) > 1 else 0
        avg_acceleration = avg_deltas[-1] - avg_deltas[-2] if len(avg_deltas) > 1 else 0

        if abs(min_acceleration) >= self.acceleration_threshold:
            insights.append(f"⚠️ 최소 임계치 변화율 급증 (변화량 {min_acceleration:.4f}) — 설비 불안정 가능성")
        if abs(max_acceleration) >= self.acceleration_threshold:
            insights.append(f"⚠️ 최대 임계치 변화율 급증 (변화량 {max_acceleration:.4f}) — 설비 불안정 가능성")
        if abs(avg_acceleration) >= self.acceleration_threshold:
            insights.append(f"⚠️ 평균 임계치 변화율 급증 (변화량 {avg_acceleration:.4f}) — 설비 불안정 가능성")

        if not insights:
            insights.append("현재 이상 징후 없음")

        return insights

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ThresholdData:
    threshold_history_no: int
    threshold_min: float
    threshold_max: float
    threshold_avg: float
    min_range_min: float
    min_range_max: float
    max_range_min: float
    max_range_max: float
    avg_range_min: float
    avg_range_max: float
    min_diff: float
    max_diff: float
    avg_diff: float
    data_count: int
    calculated_at: datetime
    sensor_data_info_no: int

    @classmethod
    def from_dict(cls, data: dict):
        # 계산된 시간 문자열을 datetime 객체로 변환
        calc_at = data.get("calculated_at")
        if isinstance(calc_at, str):
            calc_at = datetime.fromisoformat(calc_at)
        return cls(
            threshold_history_no=data.get("threshold_history_no"),
            threshold_min=data.get("threshold_min"),
            threshold_max=data.get("threshold_max"),
            threshold_avg=data.get("threshold_avg"),
            min_range_min=data.get("min_range_min"),
            min_range_max=data.get("min_range_max"),
            max_range_min=data.get("max_range_min"),
            max_range_max=data.get("max_range_max"),
            avg_range_min=data.get("avg_range_min"),
            avg_range_max=data.get("avg_range_max"),
            min_diff=data.get("min_diff"),
            max_diff=data.get("max_diff"),
            avg_diff=data.get("avg_diff"),
            data_count=data.get("data_count"),
            calculated_at=calc_at,
            sensor_data_info_no=data.get("sensor_data_info_no"),
        )

import requests
import pandas as pd
import os
from datetime import datetime
from config import SENSOR_API_URL

import logging

DATA_DIR = "data"
SENSOR_ENDPOINT = f"{SENSOR_API_URL}/api/threshold-histories"
logger = logging.getLogger(__name__)

def flatten_sensor_data(raw_data: dict) -> pd.DataFrame:
    """
    중첩된 센서 데이터를 평탄화하여 DataFrame으로 변환합니다.
    """
    records = []

    gateway_id = raw_data.get("gateway_id")
    for sensor in raw_data.get("sensors", []):
        sensor_id = sensor.get("sensor_id")
        for t in sensor.get("types", []):
            sensor_type = t.get("type_en_name") or t.get("type")
            records.append({
                "gateway_id": gateway_id,
                "sensor_id": sensor_id,
                "sensor_type": sensor_type,
                "min_diff": t.get("min_diff"),
                "max_diff": t.get("max_diff"),
                "avg_diff": t.get("avg_diff"),
                "date": pd.to_datetime(t.get("calculated_at"))
            })

    return pd.DataFrame(records)

def fetch_threshold_history(target_date: datetime = None) -> pd.DataFrame:
    """
    센서 서비스에서 임계치 변화량 데이터를 받아와 평탄화합니다.
    target_date가 None이면 오늘 날짜 기준으로 요청합니다.
    Args:
        target_date (datetime): 조회할 날짜
    Returns:
        pd.DataFrame
    """
    try:
        if target_date is None:
            target_date = datetime.now()
        date_str = target_date.strftime("%Y-%m-%d")
        url = f"{SENSOR_ENDPOINT}/{date_str}"
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        raw_data = response.json()
        return flatten_sensor_data(raw_data)
    except Exception as e:
        logger.error(f"센서 API 호출 실패: {e}", exc_info=True)
        return pd.DataFrame()

def save_unified_by_sensor_type(df: pd.DataFrame):
    """
    센서 타입별로 데이터를 하나의 CSV로 통합 저장합니다.
    """
    if df.empty:
        logger.info("저장할 데이터가 없습니다.")
        return

    os.makedirs(DATA_DIR, exist_ok=True)

    for sensor_type, group_df in df.groupby("sensor_type"):
        filename = f"{sensor_type}.csv"
        csv_path = os.path.join(DATA_DIR, filename)

        if os.path.exists(csv_path):
            existing_df = pd.read_csv(csv_path, parse_dates=["date"])
            combined_df = pd.concat([existing_df, group_df], ignore_index=True)
            combined_df.drop_duplicates(subset=["gateway_id", "sensor_id", "date"], inplace=True)
        else:
            combined_df = group_df

        combined_df.sort_values(by=["sensor_id", "date"], inplace=True)
        combined_df.to_csv(csv_path, index=False)
        logger.info(f"{sensor_type} → {len(group_df)}개 저장 완료 ({datetime.now().isoformat()})")

if __name__ == "__main__":
    # 현재 날짜를 자동으로 넣어서 호출
    df = fetch_threshold_history(datetime.now())
    save_unified_by_sensor_type(df)

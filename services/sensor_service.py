import requests
import pandas as pd
import os
from datetime import datetime
from config.settings import SENSOR_API_URL
import logging

DATA_DIR = "data/sensors"  # 센서별 폴더 구조 기준 경로
SENSOR_ENDPOINT = f"{SENSOR_API_URL}/threshold-histories/date"
logger = logging.getLogger(__name__)


def flatten_sensor_data(raw_data) -> pd.DataFrame:
    """
    중첩된 센서 데이터를 평탄화하여 DataFrame으로 변환합니다.
    raw_data는 dict 또는 list일 수 있습니다.
    """
    records = []

    # raw_data가 list이면 반복 처리
    data_list = raw_data if isinstance(raw_data, list) else [raw_data]
    
    for item in data_list:
        gateway_id = item.get("gateway_id")
        for sensor in item.get("sensors", []):
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
                    "date": pd.to_datetime(t.get("calculated_at"), unit='ms')  # 밀리초 단위 변환
                })

    return pd.DataFrame(records)


def fetch_threshold_history(target_date: datetime = None) -> pd.DataFrame:
    """
    센서 서비스에서 임계치 변화량 데이터를 받아와 평탄화합니다.
    target_date가 None이면 오늘 날짜 기준으로 요청합니다.
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


def save_by_sensor_and_type(df: pd.DataFrame):
    """
    센서 ID별 폴더 내에 타입별 CSV 파일로 저장합니다.
    기존 파일이 있으면 중복 제거 후 이어쓰기 합니다.
    """
    if df.empty:
        logger.info("저장할 데이터가 없습니다.")
        return

    for sensor_id, sensor_df in df.groupby("sensor_id"):
        sensor_dir = os.path.join(DATA_DIR, sensor_id)
        os.makedirs(sensor_dir, exist_ok=True)

        for sensor_type, group_df in sensor_df.groupby("sensor_type"):
            csv_path = os.path.join(sensor_dir, f"{sensor_type}.csv")

            if os.path.exists(csv_path):
                existing_df = pd.read_csv(csv_path, parse_dates=["date"])
                combined_df = pd.concat([existing_df, group_df], ignore_index=True)
                # 중복 제거: gateway_id, sensor_id, sensor_type, date 기준
                combined_df.drop_duplicates(subset=["gateway_id", "sensor_id", "sensor_type", "date"], inplace=True)
            else:
                combined_df = group_df

            combined_df.sort_values(by=["date"], inplace=True)
            combined_df.to_csv(csv_path, index=False)
            logger.info(f"센서 {sensor_id} - 타입 {sensor_type}: {len(group_df)}개 저장 완료 ({datetime.now().isoformat()})")


if __name__ == "__main__":
    df = fetch_threshold_history(datetime.now())
    save_by_sensor_and_type(df)

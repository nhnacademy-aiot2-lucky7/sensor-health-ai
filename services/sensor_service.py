import requests
import pandas as pd
import os
from datetime import datetime
from config import SENSOR_API_URL

# 저장 경로 및 파일 이름
DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "threshold_history.csv")

SENSOR_ENDPOINT = f"{SENSOR_API_URL}/api/v1/threshold-histories"

def fetch_threshold_history() -> pd.DataFrame:
    """
    센서 서비스에서 임계치 변화량 데이터를 받아옵니다.
    Returns:
        pd.DataFrame: 센서 데이터 (sensor_id, date, min_diff, max_diff, avg_diff)
    """
    try:
        response = requests.get(SENSOR_ENDPOINT, timeout=5)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        return df
    except Exception as e:
        print(f"[ERROR] 센서 API 호출 실패: {e}")
        return pd.DataFrame()

def save_to_csv(df: pd.DataFrame):
    """
    데이터를 CSV에 누적 저장합니다.
    이미 존재하는 레코드는 중복 저장하지 않습니다.
    """
    if df.empty:
        print("[INFO] 저장할 데이터가 없습니다.")
        return

    os.makedirs(DATA_DIR, exist_ok=True)

    # 기존 데이터 불러오기 (있다면)
    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE, parse_dates=['date'])
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.drop_duplicates(subset=["sensor_id", "date"], inplace=True)
    else:
        combined_df = df

    combined_df.sort_values(by=["sensor_id", "date"], inplace=True)
    combined_df.to_csv(CSV_FILE, index=False)
    print(f"[INFO] {len(df)}개 레코드 저장 완료 ({datetime.now().isoformat()})")

if __name__ == "__main__":
    df = fetch_threshold_history()
    save_to_csv(df)
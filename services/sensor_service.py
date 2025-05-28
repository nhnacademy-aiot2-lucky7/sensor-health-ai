import requests
import pandas as pd
from config import SENSOR_API_URL

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

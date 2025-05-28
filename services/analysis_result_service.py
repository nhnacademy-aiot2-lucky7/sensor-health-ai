import requests
import json
from config import ANALYSIS_RESULT_API_URL

ANALYSIS_RESULT_ENDPOINT = f"{ANALYSIS_RESULT_API_URL}/api"

def send_analysis_result(result: dict):
    try:
        response = requests.post(ANALYSIS_RESULT_ENDPOINT, json=result, timeout=5)
        response.raise_for_status()
        print(f"[INFO] 결과 전송 완료: {result}")
    except Exception as e:
        print(f"[ERROR] 결과 전송 실패: {e}")
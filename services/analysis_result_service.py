import requests
from config.settings import ANALYSIS_RESULT_API_URL

import logging

logger = logging.getLogger(__name__)

ANALYSIS_RESULT_ENDPOINT = f"{ANALYSIS_RESULT_API_URL}/analysis-results"

def send_analysis_result(result: dict):
    try:
        response = requests.post(ANALYSIS_RESULT_ENDPOINT, json=result, timeout=5)
        response.raise_for_status()
        logger.info(f"결과 전송 완료: {result}")
    except Exception as e:
        logger.error(f"결과 전송 실패: {e}", exc_info=True)
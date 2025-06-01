import os
from dotenv import load_dotenv

# 개발 환경에서는 .env 파일을 불러옴
if os.getenv("USE_DOTENV", "true").lower() == "true":
    load_dotenv()

SENSOR_API_URL = os.getenv("SENSOR_API_URL")
ANALYSIS_RESULT_API_URL = os.getenv("ANALYSIS_RESULT_API_URL")

# 예측 기준 시간
PREDICTION_CUTOFF_HOUR = 2  # 새벽 2시 기준
PREDICTION_LOG_FILE = "prediction_log.txt"
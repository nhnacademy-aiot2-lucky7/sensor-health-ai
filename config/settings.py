import os
import redis
from dotenv import load_dotenv

# 개발 환경에서는 .env 파일을 불러옴
if os.getenv("USE_DOTENV", "true").lower() == "true":
    load_dotenv()

SENSOR_API_URL = os.getenv("SENSOR_API_URL")
ANALYSIS_RESULT_API_URL = os.getenv("ANALYSIS_RESULT_API_URL")

# redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    db=os.getenv("REDIS_DB"),
    decode_responses=True  # 문자열로 받기 위해 설정
)
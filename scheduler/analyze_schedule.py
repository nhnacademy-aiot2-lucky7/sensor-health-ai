import logging
from models.health_predictor import predict

logger = logging.getLogger(__name__)

def _run_job(job_name: str, schedule_time: str):
    logger.info(f"{job_name} 시작 [{schedule_time}]")
    try:
        predict()
        logger.info(f"{job_name} 종료 [{schedule_time}]")
    except Exception as e:
        logger.error(f"{job_name} 중 오류 발생: {e}", exc_info=True)

def job_main():
    _run_job("메인 예측 작업", "02:30")

def job_check():
    _run_job("놓친 부분 점검 작업", "01:30")

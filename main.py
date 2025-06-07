import config.logging_setup
import time
import logging
import schedule
from config.settings import JOB_MAIN_TIME, JOB_CHECK_TIME
from scheduler.analyze_schedule import job_main, job_check
import signal
import sys

logger = logging.getLogger(__name__)

schedule.every().day.at("08:17").do(job_main)
schedule.every().day.at("08:20").do(job_check)

# 종료 신호 처리 함수
def signal_handler(sig, frame):
    logger.info("스케줄러 종료")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("스케줄러 시작")
    try:
        while True:
            logger.debug("작업 대기 중...")
            schedule.run_pending()
            time.sleep(60)
    except Exception as e:
        logger.exception(f"스케줄러 실행 중 예외 발생: {e}")
        logger.info("스케줄러 종료")
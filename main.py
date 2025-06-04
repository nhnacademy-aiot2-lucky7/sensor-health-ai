import time
import logging
import schedule
from config.settings import JOB_MAIN_TIME, JOB_CHECK_TIME
from scheduler.analyze_schedule import job_main, job_check

logger = logging.getLogger(__name__)

schedule.every().day.at(JOB_MAIN_TIME).do(job_main)
schedule.every().day.at(JOB_CHECK_TIME).do(job_check)

if __name__ == "__main__":
    logger.info("스케줄러 시작")
    while True:
        schedule.run_pending()
        time.sleep(60)
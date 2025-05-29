# scheduler.py
import logging
import signal
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from sensor_service import trigger_analysis

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()

# 안전한 job 실행을 위한 래퍼 함수
def safe_trigger_analysis(time_str):
    try:
        logger.info(f"[🚀] 센서 분석 시작: {time_str}")
        trigger_analysis(time_str)
        logger.info(f"[✅] 센서 분석 완료: {time_str}")
    except Exception as e:
        logger.error(f"[❌] 센서 분석 실패 ({time_str}): {e}")

# job 이벤트 리스너
def job_listener(event):
    if event.exception:
        logger.error(f"Job {event.job_id} 실행 중 오류: {event.exception}")
    else:
        logger.info(f"Job {event.job_id} 성공적으로 실행됨")

# 스케줄 등록
scheduler.add_job(
    lambda: safe_trigger_analysis("01:30"), 
    'cron', 
    hour=1, 
    minute=30,
    id='sensor_analysis_0130'
)
scheduler.add_job(
    lambda: safe_trigger_analysis("02:30"), 
    'cron', 
    hour=2, 
    minute=30,
    id='sensor_analysis_0230'
)

# 이벤트 리스너 등록
scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

# Graceful shutdown 처리
def signal_handler(signum, frame):
    logger.info("[🛑] 종료 신호 수신, 스케줄러 정리 중...")
    scheduler.shutdown(wait=True)
    logger.info("[👋] 스케줄러 정상 종료")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    try:
        logger.info("[🔁] 스케줄러 시작")
        logger.info("등록된 작업:")
        for job in scheduler.get_jobs():
            logger.info(f"  - {job.id}: {job.trigger}")
        
        scheduler.start()
    except Exception as e:
        logger.error(f"[💥] 스케줄러 시작 실패: {e}")
        sys.exit(1)
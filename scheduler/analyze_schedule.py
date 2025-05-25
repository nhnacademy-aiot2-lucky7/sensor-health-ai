import schedule
import time
import logging
from threading import Thread

# AI 학습 함수 (아직 구현 전이지만 임시 placeholder)
def train_incremental_model():
    logging.info("[AI] Incremental 모델 학습 시작")
    # TODO: 분석 완료된 센서 중 최근 1시간 이내 임계치 변화 데이터 가져와 학습
    # model.train_incremental(data)
    logging.info("[AI] Incremental 모델 학습 완료")

def train_daily_batch_model():
    logging.info("[AI] 일일 배치 모델 학습 시작")
    # TODO: 전체 센서 임계치 변화 추이 기반 전체 학습 수행
    # model.train_full(data)
    logging.info("[AI] 일일 배치 모델 학습 완료")

def run_async(job_func):
    t = Thread(target=job_func)
    t.daemon = True
    t.start()

def run_ai_scheduler():
    logging.basicConfig(level=logging.INFO)

    # 1시간마다 incremental 학습 (정각 + 10분)
    schedule.every().hour.at(":10").do(lambda: run_async(train_incremental_model))
    logging.info("[SCHEDULER] Incremental 모델 학습: 매시간 +10분 예약됨")

    # 매일 02:30에 배치 학습
    schedule.every().day.at("02:30").do(lambda: run_async(train_daily_batch_model))
    logging.info("[SCHEDULER] 배치 모델 학습: 매일 02:30 예약됨")

    logging.info("[SCHEDULER] AI 학습 스케줄러 시작됨")

    while True:
        schedule.run_pending()
        time.sleep(1)

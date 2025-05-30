import schedule
import time
from models.health_predictor import run_prediction

def job_main():
    print("[02:30] 메인 예측 작업 시작")
    run_prediction()
    print("[02:30] 메인 예측 작업 종료")

def job_check():
    print("[01:30] 놓친 부분 점검 작업 시작")
    run_prediction()
    print("[01:30] 놓친 부분 점검 작업 종료")

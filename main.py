from scheduler.analyze_schedule import job_main, job_check
import schedule
import time

schedule.every().day.at("01:30").do(job_check)
schedule.every().day.at("02:30").do(job_main)

if __name__ == "__main__":
    print("스케줄러 시작")
    while True:
        schedule.run_pending()
        time.sleep(60)
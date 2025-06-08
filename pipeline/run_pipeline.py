import os
import glob
import pandas as pd
from datetime import datetime
from services.sensor_service import fetch_threshold_history, save_by_sensor_and_type, DATA_DIR
from ai.health_predictor import predict
from services.analysis_result_service import send_analysis_result

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline():
    # 1. 센서 데이터 수집
    logger.info("📡 센서 임계치 데이터 수집 시작")
    df = fetch_threshold_history(datetime.now())
    
    logger.info(f"수집된 데이터: {df}")
    
    if df.empty:
        logger.warning("⚠️ 수집된 데이터가 없습니다. 파이프라인 종료")
        return

    # 2. 수집된 데이터를 센서타입별 CSV로 저장
    logger.info("💾 센서 타입별 CSV 저장")
    save_by_sensor_and_type(df)

    # 3. 저장된 모든 센서 타입별 CSV 파일을 탐색
    csv_files = glob.glob(os.path.join(DATA_DIR, "*", "*.csv"))

    if not csv_files:
        logger.warning("⚠️ 저장된 CSV 파일이 없습니다. 파이프라인 종료")
        return

    for file_path in csv_files:
        sensor_type = os.path.basename(file_path).replace(".csv", "")
        try:
            df = pd.read_csv(file_path, parse_dates=["date"])
        except Exception as e:
            logger.error(f"❌ CSV 로드 실패: {file_path} - {e}")
            continue

        # 4. 센서 단위로 예측 수행
        for (gateway_id, sensor_id), group_df in df.groupby(["gateway_id", "sensor_id"]):
            df_sensor = group_df.sort_values(by="date").dropna(subset=["min_diff", "max_diff", "avg_diff"]).tail(15)

            if df_sensor.shape[0] < 10:
                logger.warning(f"⚠️ 분석 생략 - 데이터 부족: {sensor_type}/{gateway_id}/{sensor_id} ({df_sensor.shape[0]}개)")
                continue

            try:
                result = predict(sensor_type, gateway_id, sensor_id, df_sensor)
                send_analysis_result(result)
                logger.info(f"✅ 분석 완료 및 전송: {sensor_type}/{gateway_id}/{sensor_id}")
            except Exception as e:
                logger.error(f"❌ 분석 실패: {sensor_type}/{gateway_id}/{sensor_id} - {e}")

if __name__ == "__main__":
    run_pipeline()

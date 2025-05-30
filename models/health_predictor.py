import pandas as pd
import pickle
import os
import json
import time
from datetime import datetime, timedelta, timezone
from config import settings
from heuristic_health_score import heuristic_health_score
from services.analysis_result_service import send_analysis_result

import logging
import config.logging_setup

REQUIRED_DAYS = 15
KST = timezone(timedelta(hours=9))

logger = logging.getLogger(__name__)

def get_logical_date():
    now = datetime.now()
    if now.hour < settings.PREDICTION_CUTOFF_HOUR:
        logical_date = now - timedelta(days=1)
    else:
        logical_date = now
    return logical_date.strftime("%Y-%m-%d")

def has_already_predicted(sensor_type, gateway_id, sensor_id):
    log_file = settings.PREDICTION_LOG_FILE
    if not os.path.exists(log_file):
        return False
    logical_date = get_logical_date()
    with open(log_file, "r") as f:
        for line in f:
            try:
                s_type, gw_id, s_id, date = line.strip().split(",")
                if s_type == sensor_type and gw_id == gateway_id and s_id == sensor_id and date == logical_date:
                    return True
            except ValueError:
                continue
    return False

def save_prediction_log(sensor_type, gateway_id, sensor_id):
    log_file = settings.PREDICTION_LOG_FILE
    logical_date = get_logical_date()
    with open(log_file, "a") as f:
        f.write(f"{sensor_type},{gateway_id},{sensor_id},{logical_date}\n")

def load_model(sensor_type: str, gateway_id: str, sensor_id: str):
    model_path = f"model_registry/{sensor_type}/{gateway_id}_{sensor_id}.pkl"
    if not os.path.isfile(model_path):
        logger.error(f"[ERROR] 모델 파일이 존재하지 않습니다: {model_path}")
        return None
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def predict(sensor_type: str, gateway_id: str, sensor_id: str, data: pd.DataFrame) -> dict:
    actual_days = len(data)
    analyzed_at = int(datetime.now(KST).timestamp())

    if actual_days < REQUIRED_DAYS:
        logger.info(f"[INFO] 데이터 일수 부족: {actual_days} < {REQUIRED_DAYS}")
        return {
            "result": {
                "analysisType": "THRESHOLD_DIFF_ANALYSIS",
                "sensorInfo": {
                    "gatewayId": gateway_id,
                    "sensorId": sensor_id,
                    "sensorType": sensor_type
                },
                "model": None,
                "healthScore": None,
                "analyzedAt": analyzed_at,
                "meta": {
                    "analysisStatus": "insufficient_data",
                    "failureReason": "not_enough_days",
                    "actualDataDays": actual_days,
                    "requiredData_days": REQUIRED_DAYS,
                    "analysisWindowDays": REQUIRED_DAYS
                }
            }
        }
    
    # 필요한 컬럼이 존재하는지 확인
    required_columns = ['min_diff', 'max_diff', 'avg_diff']
    if not all(col in data.columns for col in required_columns):
        logger.error(f"[ERROR] 필요 컬럼 누락: {required_columns} 중 일부가 데이터에 없습니다.")
        return {
            "result": {
                "analysisType": "THRESHOLD_DIFF_ANALYSIS",
                "sensorInfo": {
                    "gatewayId": gateway_id,
                    "sensorId": sensor_id,
                    "sensorType": sensor_type
                },
                "model": None,
                "healthScore": None,
                "analyzedAt": analyzed_at,
                "meta": {
                    "analysisStatus": "invalid_data",
                    "failureReason": "missing_required_columns",
                    "actualDataDays": actual_days,
                    "requiredData_days": REQUIRED_DAYS,
                    "analysisWindowDays": REQUIRED_DAYS
                }
            }
        }

    # 결측값 여부 확인
    if data[required_columns].isnull().values.any():
        logger.error("[ERROR] 결측치 존재: 데이터에 NULL 값이 포함되어 있습니다.")
        return {
            "result": {
                "analysisType": "THRESHOLD_DIFF_ANALYSIS",
                "sensorInfo": {
                    "gatewayId": gateway_id,
                    "sensorId": sensor_id,
                    "sensorType": sensor_type
                },
                "model": None,
                "healthScore": None,
                "analyzedAt": analyzed_at,
                "meta": {
                    "analysisStatus": "invalid_data",
                    "failureReason": "contains_null_values",
                    "actualDataDays": actual_days,
                    "requiredData_days": REQUIRED_DAYS,
                    "analysisWindowDays": REQUIRED_DAYS
                }
            }
        }

    model = load_model(sensor_type, gateway_id, sensor_id)
    x_input = data[['min_diff', 'max_diff', 'avg_diff']].mean().values.reshape(1, -1)

    if model:
        score = model.predict(x_input)[0]
        model_type = "RandomForest"
        logger.info(f"[INFO] 모델 예측 성공 - 점수: {score}")
    else:
        score = heuristic_health_score(data)
        model_type = "Heuristic-based"
        logger.info("[INFO] 모델이 없어 heuristic으로 점수 계산")

    return {
        "result": {
            "analysisType": "THRESHOLD_DIFF_ANALYSIS",
            "sensorInfo": {
                "gatewayId": gateway_id,
                "sensorId": sensor_id,
                "sensorType": sensor_type
            },
            "model": model_type,
            "healthScore": round(score, 4),
            "analyzedAt": analyzed_at,
            "meta": {
                "analysisStatus": "analyzed",
                "failureReason": None,
                "actualDataDays": actual_days,
                "requiredData_days": REQUIRED_DAYS,
                "analysisWindowDays": REQUIRED_DAYS
            }
        }
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 6:
        logger.error("[ERROR] 사용법: python health_predictor.py <csv_path> <sensor_type> <gateway_id> <sensor_id> <output_json_path>")
        sys.exit(1)

    csv_path, sensor_type, gateway_id, sensor_id, output_path = sys.argv[1:]

    try:
        df = pd.read_csv(csv_path, parse_dates=['date'])
        df_filtered = df[(df['gateway_id'] == gateway_id) & (df['sensor_id'] == sensor_id)]
        df_filtered = df_filtered.sort_values(by='date').tail(REQUIRED_DAYS)

        result = predict(sensor_type, gateway_id, sensor_id, df_filtered)

        # 저장하지 말고 바로 전송
        send_analysis_result(result)

        logger.info("[INFO] 예측 결과 전송 완료")
    except Exception as e:
        logger.error(f"[ERROR] 예측 실패: {e}")
        sys.exit(1)

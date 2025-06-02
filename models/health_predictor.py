import pandas as pd
import pickle
import os
import logging
from datetime import datetime, timedelta, timezone
from config import settings
from heuristic_health_score import heuristic_health_score
from services.analysis_result_service import send_analysis_result


REQUIRED_DAYS = 15
KST = timezone(timedelta(hours=9))

logger = logging.getLogger(__name__)

def load_model(sensor_type: str, gateway_id: str, sensor_id: str):
    model_path = f"model_registry/{sensor_type}/{gateway_id}_{sensor_id}.pkl"
    if not os.path.isfile(model_path):
        return None
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        logger.error(f"모델 로드 실패: {e}")
        return None

def save_model(model, sensor_type, gateway_id, sensor_id):
    model_dir = f"model_registry/{sensor_type}"
    os.makedirs(model_dir, exist_ok=True)
    model_path = f"{model_dir}/{gateway_id}_{sensor_id}.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"모델 저장 완료: {model_path}")

def predict(sensor_type: str, gateway_id: str, sensor_id: str, data: pd.DataFrame) -> dict:
    from model_trainer import train_model  # 🔄 조건 만족 시 내부에서 호출

    actual_days = len(data)
    analyzed_at = int(datetime.now(KST).timestamp())

    if actual_days < REQUIRED_DAYS:
        logger.info(f"데이터 일수 부족: {actual_days} < {REQUIRED_DAYS}")
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

    required_columns = ['min_diff', 'max_diff', 'avg_diff']
    if not all(col in data.columns for col in required_columns):
        logger.error(f"필요 컬럼 누락: {required_columns} 중 일부가 데이터에 없습니다.")
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

    if data[required_columns].isnull().values.any():
        logger.error("결측치 존재: 데이터에 NULL 값이 포함되어 있습니다.")
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
    x_input = data[required_columns].mean().values.reshape(1, -1)

    if model:
        score = model.predict(x_input)[0]
        model_type = "RandomForest"
        logger.info(f"모델 예측 성공 - 점수: {score}")
    else:
        # ✨ 조건 만족 시 학습 시도
        if 'health_score' in data.columns and actual_days >= REQUIRED_DAYS:
            try:
                logger.info(f"모델이 없어 학습 시도 중: {sensor_type}/{gateway_id}/{sensor_id}")
                model = train_model(data)
                save_model(model, sensor_type, gateway_id, sensor_id)
                score = model.predict(x_input)[0]
                model_type = "RandomForest (newly trained)"
                logger.info(f"새 모델 학습 및 예측 성공 - 점수: {score}")
            except Exception as e:
                logger.error(f"모델 학습 실패, 휴리스틱으로 대체: {e}")
                score = heuristic_health_score(data)
                model_type = "Heuristic-based (fallback)"
        else:
            score = heuristic_health_score(data)
            model_type = "Heuristic-based"
            logger.info("모델이 없어 heuristic으로 점수 계산")

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
        logger.error("사용법: python health_predictor.py <csv_path> <sensor_type> <gateway_id> <sensor_id> <output_json_path>")
        sys.exit(1)

    csv_path, sensor_type, gateway_id, sensor_id, output_path = sys.argv[1:]

    try:
        df = pd.read_csv(csv_path, parse_dates=['date'])
        df_filtered = df[(df['gateway_id'] == gateway_id) & (df['sensor_id'] == sensor_id)]
        df_filtered = df_filtered.sort_values(by='date').tail(REQUIRED_DAYS)

        result = predict(sensor_type, gateway_id, sensor_id, df_filtered)

        send_analysis_result(result)
        logger.info("예측 결과 전송 완료")
    except Exception as e:
        logger.error(f"예측 실패: {e}")
        sys.exit(1)

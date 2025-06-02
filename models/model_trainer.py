import pandas as pd
import pickle
import os
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 설정
REQUIRED_DAYS = 15
REQUIRED_COLUMNS = {'min_diff', 'max_diff', 'avg_diff', 'health_score'}

# 로거 설정
logger = logging.getLogger(__name__)

def validate_data(data: pd.DataFrame):
    """필수 컬럼 및 결측값 검사"""
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")
    return data.dropna(subset=['min_diff', 'max_diff', 'avg_diff'])

def train_model(data: pd.DataFrame):
    """모델 학습"""
    data = validate_data(data)

    X = data[['min_diff', 'max_diff', 'avg_diff']]
    y = data['health_score']

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    model = RandomForestRegressor(
        n_estimators=150,
        min_samples_leaf=3,
        max_features='sqrt',
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_val)
    mse = mean_squared_error(y_val, y_pred)
    logger.info(f"[모델검증] MSE = {mse:.5f}")

    return model

def save_model(model, save_path: str):
    """모델 저장"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"[모델저장] 완료: {save_path}")

def train_all_models(csv_path: str, sensor_type: str):
    """센서별 전체 모델 학습"""
    try:
        df = pd.read_csv(csv_path, parse_dates=['date'])
    except Exception as e:
        logger.error(f"[파일로드 실패] {csv_path}: {e}")
        return

    grouped = df.groupby(['gateway_id', 'sensor_id'])

    for (gateway_id, sensor_id), group in grouped:
        if len(group) < REQUIRED_DAYS:
            logger.warning(f"[데이터부족] {gateway_id}-{sensor_id}: {len(group)}일")
            continue

        logger.info(f"[학습시작] {gateway_id}-{sensor_id} - {len(group)}건")
        try:
            model = train_model(group)
            save_path = f"model_registry/{sensor_type}/{gateway_id}_{sensor_id}.pkl"
            save_model(model, save_path)
        except Exception as e:
            logger.error(f"[학습실패] {gateway_id}-{sensor_id}: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        logger.error("사용법: python model_trainer.py <csv_path> <sensor_type>")
        sys.exit(1)

    csv_path, sensor_type = sys.argv[1], sys.argv[2]
    train_all_models(csv_path, sensor_type)

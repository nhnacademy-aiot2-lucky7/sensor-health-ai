import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def train_model(data: pd.DataFrame):
    # 필수 컬럼 체크
    required_cols = {'min_diff', 'max_diff', 'avg_diff', 'health_score'}
    if not required_cols.issubset(set(data.columns)):
        missing = required_cols - set(data.columns)
        raise ValueError(f"데이터에 필요한 컬럼이 없습니다: {missing}")
    
    # NULL 제거 추가 (이 3개 컬럼 중 하나라도 NULL이면 제거)
    data = data.dropna(subset=['min_diff', 'max_diff', 'avg_diff'])
    
    # 입력과 타겟 분리
    x = data[['min_diff', 'max_diff', 'avg_diff']]
    y = data['health_score']
    
    # 학습/검증 분리
    x_train, x_val, y_train, y_val = train_test_split(
        x, y, test_size=0.2, random_state=42, shuffle=True
    )
    
    model = RandomForestRegressor(
        n_estimators=150, 
        random_state=42,
        min_samples_leaf=3,
        max_features='sqrt'
    )
    model.fit(x_train, y_train)
    
    y_pred = model.predict(x_val)
    mse = mean_squared_error(y_val, y_pred)
    print(f"[INFO] 검증 MSE: {mse:.5f}")
    
    return model

def save_model(model, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"[INFO] 모델 저장 완료: {save_path}")

def train_all_models(csv_path: str, sensor_type: str):
    df = pd.read_csv(csv_path, parse_dates=['date'])
    
    for (gateway_id, sensor_id), group in df.groupby(['gateway_id', 'sensor_id']):
        if len(group) < 15:
            print(f"[WARN] {gateway_id}-{sensor_id} 데이터 부족({len(group)}일), 학습 생략")
            continue
        
        print(f"[INFO] {gateway_id}-{sensor_id} 학습 시작, 데이터 수: {len(group)}")
        try:
            model = train_model(group)
            save_path = f"model_registry/{sensor_type}/{gateway_id}_{sensor_id}.pkl"
            save_model(model, save_path)
        except Exception as e:
            print(f"[ERROR] {gateway_id}-{sensor_id} 학습 실패: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("사용법: python model_trainer.py <csv_path> <sensor_type>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    sensor_type = sys.argv[2]
    
    train_all_models(csv_path, sensor_type)

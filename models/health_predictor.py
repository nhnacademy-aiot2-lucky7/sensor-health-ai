import joblib
from services.sensor_service import fetch_threshold_history
from services.analysis_result_service import send_sensor_status

MODEL_PATH = "model/model.joblib"

def run_analysis():
    df = fetch_threshold_history()
    if df.empty:
        print("[WARN] 분석할 데이터가 없습니다.")
        return

    X = df[['min_diff', 'max_diff', 'avg_diff']]

    loaded = joblib.load(MODEL_PATH)
    model = loaded['model']
    label_encoder = loaded['label_encoder']

    predictions = model.predict(X)
    probabilities = model.predict_proba(X).max(axis=1)

    for idx, row in df.iterrows():
        result = {
            "sensor_id": row["sensor_id"],
            "score": float(probabilities[idx]),
            "predicted_status": str(label_encoder.inverse_transform([predictions[idx]])[0])
        }
        send_analysis_result(result)

if __name__ == "__main__":
    run_analysis()

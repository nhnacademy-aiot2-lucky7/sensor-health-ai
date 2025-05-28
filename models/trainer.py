import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def train_and_save_model(train_csv_path: str, model_path: str):
    df = pd.read_csv(train_csv_path)

    X = df[['min_diff', 'max_diff', 'avg_diff']]
    y = df['status_label']

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        min_samples_leaf=2,
        max_features="sqrt"
    )
    model.fit(X, y_encoded)

    joblib.dump({
        'model': model,
        'label_encoder': label_encoder
    }, model_path)

    print(f"[INFO] 모델 저장 완료: {model_path}")

if __name__ == "__main__":
    train_and_save_model("train.csv", "model/model.joblib")

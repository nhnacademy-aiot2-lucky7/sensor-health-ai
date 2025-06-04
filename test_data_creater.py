import pandas as pd
from datetime import datetime, timedelta
import os

data = []
base_date = datetime.now() - timedelta(days=14)

for i in range(15):
    day = base_date + timedelta(days=i)
    data.append({
        "gateway_id": "gw-001",
        "sensor_id": "sensor-123",
        "sensor_type": "temperature",
        "min_diff": 0.1 + i * 0.01,
        "max_diff": 0.5 + i * 0.02,
        "avg_diff": 0.3 + i * 0.015,
        "date": day.isoformat()
    })

df = pd.DataFrame(data)
os.makedirs("test_data", exist_ok=True)
df.to_csv("test_data/test_sensor_data.csv", index=False)

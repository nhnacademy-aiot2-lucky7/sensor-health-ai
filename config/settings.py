SENSOR_SERVICE_URL = "http://sensor-service:10238/api/v1/threshold-histories"

RABBITMQ = {
    "host": "localhost",
    "port": 5672,
    "queue": "sensor_alerts",  # 보내려는 큐 이름
    "username": "guest",
    "password": "guest"
}
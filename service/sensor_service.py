import requests
import logging

SENSOR_SERVICE_BASE_URL = "http://sensor-service:10238/api/v1/threshold-histories/{gateway-id}"

def fetch_thresholds_by_sensor_ids(sensor_ids):
    """
    분석된 센서들의 임계치 데이터를 센서 API로부터 받아오는 함수

    :param sensor_ids: 센서 ID 리스트
    :return: 센서별 임계치 데이터 리스트 (JSON)
    """
    try:
        sensor_ids_param = ",".join(sensor_ids)
        url = f"{SENSOR_SERVICE_BASE_URL}/thresholds"
        params = {"sensorIds": sensor_ids_param}

        logging.info(f"[FETCH] 센서 API 호출: {url} with params {params}")
        response = requests.get(url, params=params, timeout=10)

        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

        thresholds_data = response.json()
        logging.info(f"[FETCH] 임계치 데이터 {len(thresholds_data)}개 수신됨")
        return thresholds_data

    except requests.RequestException as e:
        logging.error(f"[FETCH] 임계치 데이터 호출 실패: {e}")
        return []

import pandas as pd

# 스케일링 계수: 평균 차이(mean_diff)를 이 값으로 곱해 0~SCALE 범위로 변환
SCALE = 10

def heuristic_health_score(data: pd.DataFrame) -> float:
    # 필요한 컬럼 존재 여부 확인
    required_columns = {'min_diff', 'max_diff', 'avg_diff'}
    if not required_columns.issubset(data.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")
    
    # min, max, avg 차이 평균값 계산
    mean_diff_value = data[list(required_columns)].mean().mean()
    
    # 평균 차이를 스케일링하고 0~SCALE 사이로 클리핑
    scaled_diff_score = max(0, min(SCALE, mean_diff_value * SCALE))
    
    # 건강 점수 계산: 차이가 작을수록 건강 → 1에 가까움
    health_score = 1 - (scaled_diff_score / 100)
    
    return round(health_score, 4)

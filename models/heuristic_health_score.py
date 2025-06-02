import pandas as pd

def heuristic_health_score(data: pd.DataFrame) -> float:
    mean_diff = data[['min_diff', 'max_diff', 'avg_diff']].mean().mean()
    
    # 0~10 범위로 클리핑
    normalized = max(0, min(10, mean_diff * 10))
    
    # 100에서 빼서 정규화
    score = (100 - normalized) / 100
    return round(score, 4)

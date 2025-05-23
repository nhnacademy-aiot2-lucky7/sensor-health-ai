from datetime import datetime

class ThresholdInsightAI:
    def __init__(self, threshold_data: dict):
        self.data = threshold_data
        self.insights = []

    def analyze(self):
        self.check_avg_near_limit()
        self.check_rising_trend()
        self.check_sudden_change()
        return self.insights

    def check_avg_near_limit(self):
        avg = self.data['threshold_avg']
        max_range = self.data['avg_range_max']
        ratio = avg / max_range if max_range != 0 else 0

        if ratio >= 0.9:
            self.insights.append(
                f"⚠️ 평균 임계치가 상한선의 {round(ratio * 100, 1)}% 수준입니다. 곧 초과할 수 있습니다."
            )

    def check_rising_trend(self, threshold=3.0):
        diff = self.data['avg_diff']
        if diff is not None and diff > threshold:
            self.insights.append(
                f"📈 평균 임계치가 이전보다 {round(diff, 2)}% 상승했습니다. 상승 추세에 주의하세요."
            )

    def check_sudden_change(self, previous_diff=None, sudden_threshold=5.0):
        current_diff = self.data['avg_diff']
        if previous_diff is not None and current_diff is not None:
            delta = current_diff - previous_diff
            if delta > sudden_threshold:
                self.insights.append(
                    f"🚨 평균 임계치 변화율이 갑자기 {round(delta, 2)}% 증가했습니다. 이상 징후 가능성이 있습니다."
                )

# ✅ 예제 실행
if __name__ == "__main__":
    # 예시 threshold row (DB에서 select된 dict 형태라고 가정)
    threshold_row = {
        "threshold_avg": 78,
        "avg_range_max": 80,
        "avg_diff": 4.2,
        "threshold_history_no": 12,
        "calculated_at": datetime.now(),
        "sensor_data_info_no": 103
    }

    previous_avg_diff = 1.0  # 이전 분석 결과에서의 avg_diff

    analyzer = ThresholdInsightAI(threshold_row)
    analyzer.check_sudden_change(previous_diff=previous_avg_diff)
    insights = analyzer.analyze()

    for msg in insights:
        print(msg)

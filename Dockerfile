# 1. 공식 Python 베이스 이미지 사용 (예: Python 3.10)
FROM python:3.10-slim

# 2. 작업 디렉토리 생성
# 컨테이너 내에서 코드가 들어갈 기본 폴더 설정
WORKDIR /app

# 3. requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 전체 소스 코드 복사
COPY . .

# 5. 실행 명령어 (main.py를 실행)
ENV PYTHONPATH=/app
CMD ["python", "main.py"]

# 1. 공식 Python 베이스 이미지 사용 (예: Python 3.10)
FROM python:3.10-slim

# 2. 빌드 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. 컨테이너 내부 작업 디렉토리 지정
WORKDIR /app

# 4. requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 5. 나머지 소스코드 복사
COPY . .

# 5-1. 로그 디렉토리 생성 및 권한 설정 추가
RUN mkdir -p /logs && chmod 777 /logs

# 6. 실행 명령어 (main.py를 실행)
ENV PYTHONPATH=/app
CMD ["python", "main.py"]
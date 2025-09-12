# 베이스 이미지: Python 3.8 slim
FROM python:3.8-slim

# 작업 디렉토리 생성
WORKDIR /app/api

# 시스템 의존 패키지 설치 (필요한 경우)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY . .

# FastAPI 기본 포트
EXPOSE 8000

# 컨테이너 시작 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

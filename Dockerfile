# 베이스 이미지를 Python 3.12로 지정
FROM python:3.12-slim

# 컨테이너 안의 작업 폴더 설정
WORKDIR /app

# 라이브러리 설치를 위해 requirements.txt 파일 먼저 복사
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 프로젝트 파일들을 전부 복사
COPY . .

# 컨테이너가 시작될 때 run.py를 실행하여 Flask 앱 구동
CMD ["python", "run.py"]

    

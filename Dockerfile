# 베이스 이미지를 Python 3.12로 지정
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY ./app /app/app

# Uvicorn 서버 실행
# --host 0.0.0.0 : 컨테이너 외부에서 접속 허용
# --port 8000 : 8000번 포트 사용
# --reload : 코드가 변경되면 서버 자동 재시작 (개발용)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
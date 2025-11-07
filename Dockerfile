# 부모 이미지로 공식 Python 런타임을 사용합니다.
FROM python:3.14-slim

# 컨테이너 내 작업 디렉토리를 설정합니다.
WORKDIR /app

# 현재 디렉토리의 모든 내용을 컨테이너의 /app 디렉토리로 복사합니다.
COPY . /app

# requirements.txt에 지정된 모든 필요한 패키지를 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너 외부에서 5000번 포트를 사용할 수 있도록 노출합니다.
EXPOSE 5000

# Flask 애플리케이션의 진입점을 환경 변수로 정의합니다.
ENV FLASK_APP=main:app

# 컨테이너가 시작될 때 Flask 애플리케이션을 실행합니다.
# 호스트 0.0.0.0으로 설정하여 외부 접속을 허용합니다.
CMD ["flask", "run", "--host=0.0.0.0"]


# 표준 시간 정의
ENV TZ=Asia/Seoul
RUN apt-get update && apt-get install -y tzdata
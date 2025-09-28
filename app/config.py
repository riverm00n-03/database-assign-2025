"""
애플리케이션의 설정을 관리함.
.env 파일로부터 환경 변수를 불러와 파이썬 변수로 정의하는 역할을 함.
"""
import os
from dotenv import load_dotenv

# .env 파일에 정의된 환경 변수들을 불러옴.
load_dotenv()

# docker-compose.yml에 정의된 DB 서비스의 호스트 이름임. 기본값은 'db'.
DB_HOST = os.environ.get('MYSQL_HOST', 'db')

# DB 서비스의 포트 번호임. 기본값은 3306.
DB_PORT = int(os.environ.get('MYSQL_PORT', 3306))

# DB에 접속할 사용자 이름임.
DB_USER = os.environ.get('MYSQL_USER')

# DB 사용자의 비밀번호임.
DB_PASSWORD = os.environ.get('MYSQL_PASSWORD')

# 접속할 데이터베이스의 이름임.
DB_NAME = os.environ.get('MYSQL_DATABASE')
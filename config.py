import os
from dotenv import load_dotenv

load_dotenv()

# config.py

# 데이터베이스 연결을 위한 설정 정보
# 이 딕셔너리를 app과 admin_cli에서 모두 import하여 사용합니다.
def get_env_variable(name):
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"환경 변수 '{name}'가 설정되지 않았습니다. .env 파일을 확인하거나 환경 변수를 설정해주세요.")
    return value

DB_CONFIG = {
    'host': get_env_variable('DB_HOST'),
    'user': get_env_variable('DB_USER'),
    'password': get_env_variable('DB_PASSWORD'),
    'database': get_env_variable('DB_NAME')
}

# 여기에 Flask 시크릿 키 등 다른 프로젝트 설정도 추가할 수 있습니다.
# SECRET_KEY = 'my-super-secret-key'
import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(name):
    """
    환경 변수를 가져옵니다.
    .env 파일에서 환경 변수를 읽어옵니다.
    
    Args:
        name: 환경 변수 이름
        
    Returns:
        환경 변수 값
        
    Raises:
        ValueError: 환경 변수가 설정되지 않은 경우
    """
    value = os.getenv(name)
    # 환경 변수가 없으면 에러 발생
    if value is None:
        raise ValueError(f"환경 변수 '{name}'가 설정되지 않았습니다. .env 파일을 확인하거나 환경 변수를 설정해주세요.")
    return value


# 데이터베이스 연결 설정
# app과 admin_cli에서 모두 import하여 사용합니다.
DB_CONFIG = {
    'host': get_env_variable('DB_HOST'),
    'user': get_env_variable('DB_USER'),
    'password': get_env_variable('DB_PASSWORD'),
    'database': get_env_variable('DB_NAME')
}
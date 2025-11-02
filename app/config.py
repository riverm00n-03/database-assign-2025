import os

# .env 파일에서 환경 변수를 로드합니다. (개발 환경에서만 필요)
# production 환경에서는 환경 변수가 직접 설정되어야 합니다.
from dotenv import load_dotenv
load_dotenv()

# 데이터베이스 연결을 위한 설정 정보
# 이 딕셔너리는 app과 admin_cli에서 모두 import하여 사용합니다.
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '비밀번호'), # 실제 비밀번호는 .env 파일에 설정하세요.
    'database': os.getenv('DB_NAME', 'wcheck')
}

# Flask 애플리케이션 시크릿 키
# 보안을 위해 이 값은 반드시 환경 변수로 설정해야 합니다.
SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key') # 실제 시크릿 키는 .env 파일에 설정하세요.
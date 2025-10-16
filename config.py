# config.py

# 데이터베이스 연결을 위한 설정 정보
# 이 딕셔너리를 app과 admin_cli에서 모두 import하여 사용합니다.
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'wcheck'
}

# 여기에 Flask 시크릿 키 등 다른 프로젝트 설정도 추가할 수 있습니다.
# SECRET_KEY = 'my-super-secret-key'
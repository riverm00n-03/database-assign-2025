import os
from dotenv import load_dotenv

# .env 파일의 내용을 환경변수로 로드
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key' # 플라스크 비밀 키. 
    # 필요한 경우 차차 추가함.

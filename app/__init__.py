from flask import Flask
from config import Config
from .database import core as db_core

def create_app(config_class=Config):
    """Flask 애플리케이션 생성 함수 (Application Factory)"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 요청이 끝날 때마다 DB 연결을 자동으로 닫도록 설정
    app.teardown_appcontext(db_core.close_db)

    # routes.py에 정의된 URL 경로들을 앱에 등록
    from . import routes
    app.register_blueprint(routes.bp)

    return app

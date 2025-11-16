import os
from flask import Flask
from config import DB_CONFIG
from app.routes.main_routes import main_bp
from app.routes.auth_routes import auth_bp
from app.routes.timetable_routes import timetable_bp
from app.routes.database_routes import db_bp
from app.routes.attendance_routes import attendance_bp
from app.routes.professor_routes import professor_bp

# Flask 애플리케이션 생성
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
# 시크릿 키는 환경 변수에서 가져오거나 개발용 기본값 사용
# 프로덕션 환경에서는 반드시 환경 변수로 설정해야 합니다.
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Blueprint 등록
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(timetable_bp)
app.register_blueprint(db_bp, url_prefix='/db')
app.register_blueprint(attendance_bp)
app.register_blueprint(professor_bp)

if __name__ == '__main__':
    # 개발 서버 실행 (프로덕션에서는 WSGI 서버 사용)
    app.run(host='0.0.0.0', port=5000, debug=True)
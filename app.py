from flask import Flask
from config import DB_CONFIG
from app.routes.main_routes import main_bp
from app.routes.auth_routes import auth_bp
from app.routes.database_routes import db_bp

app = Flask(__name__) # Flask 애플리케이션 인스턴스 생성
app.secret_key = 'your_secret_key' # 세션 관리를 위한 secret key 설정

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth') # Prefix for auth routes
app.register_blueprint(db_bp, url_prefix='/db') # Prefix for database routes

if __name__ == '__main__':
    app.run(debug=True)
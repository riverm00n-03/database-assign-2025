from flask import Flask
from config import DB_CONFIG
from app.routes.main_routes import main_bp
from app.routes.auth_routes import auth_bp
from app.routes.timetable_routes import timetable_bp
from app.routes.database_routes import db_bp
from app.routes.attendance_routes import attendance_bp
from app.routes.professor_routes import professor_bp

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = 'your_secret_key'

# Blueprint 등록
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(timetable_bp)
app.register_blueprint(db_bp, url_prefix='/db')
app.register_blueprint(attendance_bp)
app.register_blueprint(professor_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
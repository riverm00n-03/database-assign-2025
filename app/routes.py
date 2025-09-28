from flask import Blueprint, jsonify
from .database import core as db_core

# 'main'이라는 이름의 블루프린트 생성
bp = Blueprint('main', __name__)

@bp.route('/')
def hello_world():
    """가장 기본적인 'Hello World'를 반환하는 라우트"""
    return "Hello World"

@bp.route('/init-db')
def init_db():
    """DB에 테이블들을 생성하는 라우트"""
    try:
        db_core.init_tables()
        return jsonify({"status": "success", "message": "데이터베이스 테이블이 성공적으로 생성되었습니다."})
    except Exception as e:
        # 오류 발생 시 에러 메시지 반환
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/check-db')
def check_db_schema():
    """생성된 DB 테이블들의 구조를 확인하는 라우트"""
    try:
        schema = db_core.get_db_schema()
        return jsonify(schema)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

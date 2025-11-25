"""
세션 관련 유틸리티 함수들
"""
from flask import session


def get_session_info():
    """
    세션에서 사용자 정보를 가져옵니다.
    
    Returns:
        dict: 사용자 정보 딕셔너리
            - username: 사용자 이름 (기본값: '사용자')
            - role: 역할 ('student' 또는 'professor', 기본값: 'student')
            - user_id: 사용자 ID
            - student_number: 학번 (학생인 경우만)
    """
    return {
        'username': session.get('username', '사용자'),
        'role': session.get('role', 'student'),
        'user_id': session.get('user_id'),
        'student_number': session.get('student_number')
    }


def get_student_session_info():
    """
    학생 세션 정보를 가져옵니다.
    
    Returns:
        dict: 학생 정보 딕셔너리
            - username: 학생 이름 (기본값: '학생')
            - role: 역할 (기본값: 'student')
            - student_number: 학번
    """
    return {
        'username': session.get('username', '학생'),
        'role': session.get('role', 'student'),
        'student_number': session.get('student_number')
    }


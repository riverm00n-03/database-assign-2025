# admin_cli/commands/user_manage.py

def list_students():
    """모든 학생의 목록을 조회하여 출력합니다."""
    print("모든 학생 목록을 조회하는 로직을 구현해야 합니다.")
    pass

def add_student(student_id, name, major, grade_str):
    """새로운 학생을 DB에 추가합니다."""
    print(f"'{name}' 학생을 추가하는 로직을 구현해야 합니다.")
    pass

def update_student(student_id, field, value):
    """특정 학생의 정보를 수정합니다."""
    print(f"'{student_id}' 학생의 정보를 수정하는 로직을 구현해야 합니다.")
    pass

def delete_student(student_id):
    """특정 학생을 DB에서 삭제합니다."""
    print(f"'{student_id}' 학생을 삭제하는 로직을 구현해야 합니다.")
    pass

# --- 교수 CRUD 함수들 ---
def list_professors(): pass
def add_professor(professor_id, name, major=None): pass
def update_professor(professor_id, field, value): pass
def delete_professor(professor_id): pass
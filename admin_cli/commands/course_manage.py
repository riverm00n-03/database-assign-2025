# admin_cli/commands/course_manage.py

def list_subjects():
    """모든 과목의 목록을 조회하여 출력합니다."""
    print("모든 과목 목록을 조회하는 로직을 구현해야 합니다.")
    pass

def add_subject(name, year_str, semester_str, prof_id): pass
def update_subject(subject_id_str, field, value): pass
def delete_subject(subject_id_str): pass

# --- 스케줄 CRUD 함수들 ---
def list_schedules(subject_id_str): pass
def add_schedule(subject_id_str, day, start_time, end_time, location): pass
def update_schedule(schedule_id_str, field, value): pass
def delete_schedule(schedule_id_str): pass

# --- 수업 세션 생성 ---
def generate_sessions(subject_id_str):
    """특정 과목의 학기 전체 수업(Class_Session)을 자동으로 생성합니다."""
    print(f"'{subject_id_str}'번 과목의 전체 수업 생성을 시작합니다...")
    pass
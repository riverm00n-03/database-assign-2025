from flask import Blueprint, render_template, session
from app.utils.auth import login_required
from app.utils.db_helpers import get_db_connection, to_time
from app.utils.session_helpers import get_session_info
from app.utils.constants import WEEKDAY_TO_STR, KOREAN_TO_WEEKDAY, WEEKDAY_NAMES
from mysql.connector import Error
from datetime import time, datetime, date

timetable_bp = Blueprint('timetable', __name__, url_prefix='/timetable')


@timetable_bp.route('/')
@login_required
def timetable():
    """
    사용자의 시간표 페이지를 표시합니다.
    학생인 경우 수강 과목, 교수인 경우 담당 과목의 시간표를 보여줍니다.
    """
    session_info = get_session_info()
    username = session_info['username']
    role = session_info['role']
    user_id = session_info['user_id']

    error = None

    try:
        with get_db_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = ""
                params = (user_id,)

                # 역할에 따라 다른 쿼리 사용
                if role == 'student':
                    # 학생이 수강하는 과목의 스케줄 정보 조회
                    query = """
                        SELECT s.name AS subject_name, p.name AS professor_name, ss.day_of_week,
                               ss.start_time, ss.end_time, ss.location
                        FROM enrollment e
                        JOIN subject s ON e.subject_id = s.subject_id
                        JOIN subject_schedule ss ON s.subject_id = ss.subject_id
                        LEFT JOIN professor p ON s.professor_id = p.professor_id
                        WHERE e.student_id = %s
                    """
                elif role == 'professor':
                    # 교수가 담당하는 과목의 스케줄 정보 조회
                    query = """
                        SELECT s.name AS subject_name, p.name AS professor_name, ss.day_of_week,
                               ss.start_time, ss.end_time, ss.location
                        FROM subject s
                        JOIN subject_schedule ss ON s.subject_id = ss.subject_id
                        JOIN professor p ON s.professor_id = p.professor_id
                        WHERE p.professor_id = %s
                    """

                # 쿼리가 설정된 경우 실행
                if query:
                    cursor.execute(query, params)
                
                schedules = cursor.fetchall()

                # 30분 단위 시간 슬롯 생성 (9:00~21:30)
                slots = [(h, m) for h in range(9, 22) for m in (0, 30)]
                # 시간표 그리드 초기화
                timetable_grid = {
                    slot: {day: None for day in WEEKDAY_NAMES[:5]}  # 월~금만 사용
                    for slot in slots
                }

                # 각 스케줄을 시간표 그리드에 배치
                for item in schedules:
                    # 요일 형식 통일 (한글 -> 영문)
                    item['day_of_week'] = KOREAN_TO_WEEKDAY.get(item['day_of_week'], item['day_of_week'])

                    # 시간을 초 단위로 변환
                    start_total_seconds = item['start_time'].total_seconds()
                    end_total_seconds = item['end_time'].total_seconds()

                    # 시작 시간 계산
                    start_hour = int(start_total_seconds // 3600)
                    start_minute = int((start_total_seconds % 3600) // 60)
                    # 수업 시간 계산 (분 단위)
                    duration_minutes = (end_total_seconds - start_total_seconds) / 60

                    # rowspan 계산 (30분 단위)
                    rowspan = int(duration_minutes / 30)

                    # 시작 시간 슬롯에 수업 정보 배치
                    if (start_hour, start_minute) in timetable_grid:
                        timetable_grid[(start_hour, start_minute)][item['day_of_week']] = {
                            **item, 'rowspan': rowspan
                        }

                    # 병합된 셀의 다음 슬롯들을 skip으로 표시
                    current_hour, current_minute = start_hour, start_minute
                    for i in range(1, rowspan):
                        current_minute += 30
                        # 60분을 넘어가면 시간 증가
                        if current_minute >= 60:
                            current_hour += 1
                            current_minute -= 60
                        # 해당 슬롯을 skip으로 표시
                        if (current_hour, current_minute) in timetable_grid:
                            timetable_grid[(current_hour, current_minute)][item['day_of_week']] = 'skip'

                # 현재 수업과 다음 수업 계산
                current_class = None
                next_class = None
                today_classes = []  # 오늘의 모든 수업 목록
                
                # 오늘 날짜와 현재 시간
                today = date.today()
                now = datetime.now()
                current_time = now.time()
                current_weekday = now.weekday()  # 0=월요일, 1=화요일, ...
                
                # 요일 매핑 (Python weekday -> DB 요일)
                today_day = WEEKDAY_TO_STR.get(current_weekday)
                
                if today_day:
                    # 오늘 날짜에 실제로 진행되는 수업만 조회 (class_session 테이블 조인)
                    today_query = ""
                    if role == 'student':
                        today_query = """
                            SELECT s.name AS subject_name, p.name AS professor_name, ss.day_of_week,
                                   ss.start_time, ss.end_time, ss.location, cs.class_date, cs.is_cancelled
                            FROM enrollment e
                            JOIN subject s ON e.subject_id = s.subject_id
                            JOIN subject_schedule ss ON s.subject_id = ss.subject_id
                            JOIN class_session cs ON ss.schedule_id = cs.schedule_id
                            LEFT JOIN professor p ON s.professor_id = p.professor_id
                            WHERE e.student_id = %s
                              AND cs.class_date = %s
                              AND cs.is_cancelled = FALSE
                        """
                    elif role == 'professor':
                        today_query = """
                            SELECT s.name AS subject_name, p.name AS professor_name, ss.day_of_week,
                                   ss.start_time, ss.end_time, ss.location, cs.class_date, cs.is_cancelled
                            FROM subject s
                            JOIN subject_schedule ss ON s.subject_id = ss.subject_id
                            JOIN class_session cs ON ss.schedule_id = cs.schedule_id
                            JOIN professor p ON s.professor_id = p.professor_id
                            WHERE p.professor_id = %s
                              AND cs.class_date = %s
                              AND cs.is_cancelled = FALSE
                        """
                    
                    # 오늘의 실제 수업 조회
                    today_schedules = []
                    if today_query:
                        cursor.execute(today_query, (user_id, today))
                        today_schedules = cursor.fetchall()
                    
                    # 요일 형식 통일 (한글 -> 영문)
                    for schedule in today_schedules:
                        schedule['day_of_week'] = KOREAN_TO_WEEKDAY.get(schedule['day_of_week'], schedule['day_of_week'])
                    
                    # 오늘의 모든 수업을 시간 순으로 정렬하여 리스트 생성
                    for schedule in today_schedules:
                        start_time = to_time(schedule['start_time'])
                        end_time = to_time(schedule['end_time'])
                        
                        # 남은 시간 계산
                        start_datetime = datetime.combine(today, start_time)
                        time_diff = start_datetime - now
                        total_minutes = int(time_diff.total_seconds() / 60)
                        hours_until = total_minutes // 60
                        minutes_until = total_minutes % 60
                        
                        class_info = {
                            'subject_name': schedule['subject_name'],
                            'professor_name': schedule.get('professor_name', ''),
                            'location': schedule.get('location', ''),
                            'start_time': start_time.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                            'hours_until': hours_until,
                            'minutes_until': minutes_until,
                            'is_current': False,
                            'is_past': end_time < current_time
                        }
                        
                        # 현재 진행 중인 수업인지 확인
                        if start_time <= current_time <= end_time:
                            class_info['is_current'] = True
                            current_class = {
                                'subject_name': schedule['subject_name'],
                                'professor_name': schedule.get('professor_name', ''),
                                'location': schedule.get('location', ''),
                                'start_time': start_time.strftime('%H:%M'),
                                'end_time': end_time.strftime('%H:%M')
                            }
                        
                        today_classes.append(class_info)
                    
                    # 시간 순으로 정렬
                    today_classes.sort(key=lambda x: x['start_time'])
                    
                    # 다음 수업 찾기 (현재 시간 이후)
                    # 현재 수업이 있어도 다음 수업을 찾아야 함
                    future_schedules = []
                    
                    for schedule in today_schedules:
                        start_time = to_time(schedule['start_time'])
                        end_time = to_time(schedule['end_time'])
                        
                        # 현재 수업이 있는 경우: 현재 수업과 다른 수업이고, 현재 수업 종료 시간 이후에 시작하는 수업
                        # 현재 수업이 없는 경우: 현재 시간 이후에 시작하는 수업
                        if current_class:
                            current_start = to_time(current_class['start_time'])
                            current_end = to_time(current_class['end_time'])
                            # 현재 수업과 다른 수업이고, 현재 수업 종료 시간 이후에 시작하는 수업
                            if start_time != current_start or end_time != current_end:
                                if start_time > current_end:
                                    future_schedules.append(schedule)
                        else:
                            # 현재 시간 이후에 시작하는 수업
                            if start_time > current_time:
                                future_schedules.append(schedule)
                    
                    if future_schedules:
                        # 가장 가까운 수업 선택
                        next_schedule = min(future_schedules, 
                                          key=lambda s: to_time(s['start_time']))
                        start_time = to_time(next_schedule['start_time'])
                        end_time = to_time(next_schedule['end_time'])
                        
                        # 남은 시간 계산
                        start_datetime = datetime.combine(today, start_time)
                        time_diff = start_datetime - now
                        total_minutes = int(time_diff.total_seconds() / 60)
                        hours_until = total_minutes // 60
                        minutes_until = total_minutes % 60
                        
                        next_class = {
                            'subject_name': next_schedule['subject_name'],
                            'professor_name': next_schedule.get('professor_name', ''),
                            'location': next_schedule.get('location', ''),
                            'start_time': start_time.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                            'hours_until': hours_until,
                            'minutes_until': minutes_until
                        }
                        
                        # 디버깅: next_class 정보 확인
                        # print(f"DEBUG: next_class = {next_class}")
                        # print(f"DEBUG: today_classes count = {len(today_classes)}")
                        # for tc in today_classes:
                        #     print(f"  - {tc['subject_name']} {tc['start_time']}-{tc['end_time']} (current: {tc.get('is_current', False)})")

    except Error as e:
        # 에러 발생 시 빈 시간표 반환
        error = f"데이터베이스 오류: {e}"
        slots = [(h, m) for h in range(9, 22) for m in (0, 30)]
        timetable_grid = {
            slot: {day: None for day in WEEKDAY_NAMES[:5]}  # 월~금만 사용
            for slot in slots
        }
        current_class = None
        next_class = None
        today_classes = []
        remaining_classes = []
    
    # 현재 수업과 다음 수업을 제외한 남은 수업 목록 생성
    remaining_classes = []
    if today_classes:
        # next_class의 시작 시간을 기준으로 비교용 변수 준비
        next_start_time = None
        next_end_time = None
        next_subject_name = None
        if next_class:
            next_start_time = next_class['start_time']
            next_end_time = next_class['end_time']
            next_subject_name = next_class['subject_name']
        
        for class_item in today_classes:
            # 현재 수업이면 제외
            if class_item.get('is_current', False):
                continue
            
            # 다음 수업과 일치하는지 확인
            # 과목명, 시작시간, 종료시간 모두 일치해야 함
            is_next_class = False
            if next_class and next_start_time and next_end_time and next_subject_name:
                if (class_item['subject_name'] == next_subject_name and
                    class_item['start_time'] == next_start_time and
                    class_item['end_time'] == next_end_time):
                    is_next_class = True
            
            # 다음 수업이 아닌 경우에만 추가
            if not is_next_class:
                remaining_classes.append(class_item)
    
    return render_template(
        'time_table.html',
        username=username,
        role=role,
        current_page='시간표',
        timetable=timetable_grid,
        error=error,
        days=WEEKDAY_NAMES[:5],  # 월~금만 사용
        current_class=current_class,
        next_class=next_class,
        today_classes=today_classes if 'today_classes' in locals() else [],
        remaining_classes=remaining_classes
    )

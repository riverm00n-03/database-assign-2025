"""
자동 결석 처리 유틸리티
23시 59분에 그날 출석 데이터가 없는 경우 자동으로 결석 처리
"""
from datetime import datetime, date
from app.utils.db_helpers import get_db_connection


def mark_absent_for_missing_checkins(target_date=None):
    """
    특정 날짜의 출석 기록이 없는 학생들을 자동으로 결석 처리합니다.
    
    Args:
        target_date: 처리할 날짜 (date 객체). None이면 오늘 날짜 사용.
    
    Returns:
        (processed_count, absent_count) 튜플
        - processed_count: 처리된 세션 수
        - absent_count: 결석 처리된 학생 수
    """
    if target_date is None:
        target_date = date.today()
    
    processed_count = 0
    absent_count = 0
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # 해당 날짜의 모든 수업 세션 조회 (휴강 제외)
                cursor.execute("""
                    SELECT cs.session_id, cs.schedule_id, cs.class_date, cs.is_cancelled
                    FROM class_session cs
                    WHERE cs.class_date = %s
                      AND cs.is_cancelled = FALSE
                """, (target_date,))
                sessions = cursor.fetchall()
                
                for session in sessions:
                    session_id = session['session_id']
                    schedule_id = session['schedule_id']
                    
                    # 해당 세션의 과목 ID 조회
                    cursor.execute("""
                        SELECT ss.subject_id
                        FROM subject_schedule ss
                        WHERE ss.schedule_id = %s
                    """, (schedule_id,))
                    schedule_result = cursor.fetchone()
                    
                    if not schedule_result:
                        continue
                    
                    subject_id = schedule_result['subject_id']
                    
                    # 해당 과목을 수강하는 모든 학생 조회
                    cursor.execute("""
                        SELECT e.student_id
                        FROM enrollment e
                        WHERE e.subject_id = %s
                    """, (subject_id,))
                    enrolled_students = cursor.fetchall()
                    
                    for student in enrolled_students:
                        student_id = student['student_id']
                        
                        # 해당 학생의 출석 기록 확인
                        cursor.execute("""
                            SELECT checkin_id
                            FROM checkin
                            WHERE session_id = %s AND student_id = %s
                        """, (session_id, student_id))
                        existing_checkin = cursor.fetchone()
                        
                        # 출석 기록이 없으면 결석 처리
                        if not existing_checkin:
                            cursor.execute("""
                                INSERT INTO checkin (session_id, student_id, status, check_time)
                                VALUES (%s, %s, 'ABSENT', NOW())
                            """, (session_id, student_id))
                            absent_count += 1
                    
                    processed_count += 1
                
                conn.commit()
                
    except Exception as e:
        print(f"자동 결석 처리 중 오류 발생: {e}")
        raise
    
    return processed_count, absent_count


def run_daily_auto_absent():
    """
    일일 자동 결석 처리 함수
    오늘 날짜의 미출석 학생들을 결석으로 처리합니다.
    
    Returns:
        (processed_count, absent_count) 튜플
    """
    today = date.today()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 자동 결석 처리 시작: {today}")
    
    try:
        processed_count, absent_count = mark_absent_for_missing_checkins(today)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 자동 결석 처리 완료: {processed_count}개 세션, {absent_count}명 결석 처리")
        return processed_count, absent_count
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 자동 결석 처리 실패: {e}")
        raise


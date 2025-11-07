# admin.py
# 콘솔 환경에서 데이터베이스를 관리하기 위한 파일

import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mysql.connector import connect
from config import DB_CONFIG

# 데이터베이스 리셋 함수
def reset_database():
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                # wcheck 데이터베이스 사용
                cursor.execute("USE wcheck")
                cursor.execute("DROP DATABASE IF EXISTS wcheck")
                cursor.execute("CREATE DATABASE wcheck")
                cursor.execute("USE wcheck")
                cursor.execute("CREATE TABLE student (student_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, student_number VARCHAR(50) NOT NULL UNIQUE, student_major VARCHAR(100), student_grade INT UNSIGNED, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                cursor.execute("CREATE TABLE professor (professor_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, major VARCHAR(100), email VARCHAR(100) UNIQUE, office_location VARCHAR(100), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                cursor.execute("CREATE TABLE subject (subject_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, professor_id INT UNSIGNED DEFAULT NULL, name VARCHAR(255) NOT NULL, subject_year INT UNSIGNED, subject_semester INT UNSIGNED, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (professor_id) REFERENCES professor(professor_id) ON DELETE SET NULL)")
                cursor.execute("CREATE TABLE subject_schedule (schedule_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, subject_id INT UNSIGNED NOT NULL, day_of_week ENUM('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN') NOT NULL, start_time TIME NOT NULL, end_time TIME NOT NULL, location VARCHAR(100), FOREIGN KEY (subject_id) REFERENCES subject(subject_id) ON DELETE CASCADE)")
                cursor.execute("CREATE TABLE enrollment (student_id INT UNSIGNED NOT NULL, subject_id INT UNSIGNED NOT NULL, registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (student_id, subject_id), FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE, FOREIGN KEY (subject_id) REFERENCES subject(subject_id) ON DELETE CASCADE)")
                cursor.execute("CREATE TABLE class_session (session_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, schedule_id INT UNSIGNED NOT NULL, class_date DATE NOT NULL, is_cancelled BOOLEAN DEFAULT FALSE, UNIQUE KEY (schedule_id, class_date), FOREIGN KEY (schedule_id) REFERENCES subject_schedule(schedule_id) ON DELETE CASCADE)")
                cursor.execute("CREATE TABLE checkin (checkin_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, session_id INT UNSIGNED NOT NULL, student_id INT UNSIGNED NOT NULL, check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status ENUM('PRESENT', 'LATE', 'ABSENT') DEFAULT 'PRESENT', UNIQUE KEY (session_id, student_id), FOREIGN KEY (session_id) REFERENCES class_session(session_id) ON DELETE CASCADE, FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE)")
                # commit
                print("DB 리셋 완료")
                return 0;
    except Exception as e:
        print("DB 리셋 과정 중 오류 발생 : ", e)
        return 1;

# 테스트 데이터 삽입 함수
def test_database():
    try:
        # 먼저 데이터베이스 리셋
        reset_result = reset_database()
        if reset_result != 0:
            print("데이터베이스 리셋 실패")
            return 1
        
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE wcheck")
                
                # 교수 3명 추가
                print("교수 데이터 삽입 중...")
                cursor.execute("INSERT INTO professor (name, major, email, office_location) VALUES (%s, %s, %s, %s)", 
                              ("김교수", "컴퓨터공학", "kim@university.ac.kr", "301호"))
                cursor.execute("INSERT INTO professor (name, major, email, office_location) VALUES (%s, %s, %s, %s)", 
                              ("이교수", "전자공학", "lee@university.ac.kr", "402호"))
                cursor.execute("INSERT INTO professor (name, major, email, office_location) VALUES (%s, %s, %s, %s)", 
                              ("박교수", "정보통신공학", "park@university.ac.kr", "203호"))
                
                # 학생 10명 추가
                print("학생 데이터 삽입 중...")
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("홍길동", "2021001", "컴퓨터공학", 1))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("김철수", "2021002", "컴퓨터공학", 1))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("이영희", "2021003", "전자공학", 2))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("박민수", "2021004", "정보통신공학", 2))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("최지영", "2021005", "컴퓨터공학", 3))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("정수진", "2021006", "전자공학", 3))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("강동현", "2021007", "정보통신공학", 4))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("윤서연", "2021008", "컴퓨터공학", 4))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("임태영", "2021009", "전자공학", 1))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("한소미", "2021010", "정보통신공학", 2))
                
                # 과목 4개 추가
                print("과목 데이터 삽입 중...")
                cursor.execute("INSERT INTO subject (name, subject_year, subject_semester, professor_id) VALUES (%s, %s, %s, %s)", 
                              ("데이터베이스", 2025, 1, 1))
                cursor.execute("INSERT INTO subject (name, subject_year, subject_semester, professor_id) VALUES (%s, %s, %s, %s)", 
                              ("운영체제", 2025, 1, 1))
                cursor.execute("INSERT INTO subject (name, subject_year, subject_semester, professor_id) VALUES (%s, %s, %s, %s)", 
                              ("디지털회로", 2025, 1, 2))
                cursor.execute("INSERT INTO subject (name, subject_year, subject_semester, professor_id) VALUES (%s, %s, %s, %s)", 
                              ("네트워크프로그래밍", 2025, 1, 3))
                
                # 과목 스케줄 추가
                print("과목 스케줄 데이터 삽입 중...")
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (1, "MON", "09:00:00", "10:30:00", "101호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (1, "WED", "09:00:00", "10:30:00", "101호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (2, "TUE", "10:30:00", "12:00:00", "102호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (2, "THU", "10:30:00", "12:00:00", "102호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (3, "MON", "13:00:00", "14:30:00", "201호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (3, "WED", "13:00:00", "14:30:00", "201호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (4, "TUE", "14:30:00", "16:00:00", "202호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (4, "THU", "14:30:00", "16:00:00", "202호"))
                
                # 수강 등록 추가
                print("수강 등록 데이터 삽입 중...")
                # 학생 1-5명이 과목 1 수강
                for student_id in range(1, 6):
                    cursor.execute("INSERT INTO enrollment (student_id, subject_id) VALUES (%s, %s)", (student_id, 1))
                # 학생 3-7명이 과목 2 수강
                for student_id in range(3, 8):
                    cursor.execute("INSERT INTO enrollment (student_id, subject_id) VALUES (%s, %s)", (student_id, 2))
                # 학생 1-4, 9-10명이 과목 3 수강
                for student_id in [1, 2, 3, 4, 9, 10]:
                    cursor.execute("INSERT INTO enrollment (student_id, subject_id) VALUES (%s, %s)", (student_id, 3))
                # 학생 5-10명이 과목 4 수강
                for student_id in range(5, 11):
                    cursor.execute("INSERT INTO enrollment (student_id, subject_id) VALUES (%s, %s)", (student_id, 4))
                
                # 수업 세션 추가 (2025년 3월 첫 주 수업들)
                print("수업 세션 데이터 삽입 중...")
                # 과목 1 (월요일, 수요일) - 3월 3일(월), 3월 5일(수)
                cursor.execute("INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, %s)", (1, "2025-03-03", False))
                cursor.execute("INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, %s)", (2, "2025-03-05", False))
                # 과목 2 (화요일, 목요일) - 3월 4일(화), 3월 6일(목)
                cursor.execute("INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, %s)", (3, "2025-03-04", False))
                cursor.execute("INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, %s)", (4, "2025-03-06", False))
                # 과목 3 (월요일, 수요일) - 3월 3일(월), 3월 5일(수)
                cursor.execute("INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, %s)", (5, "2025-03-03", False))
                cursor.execute("INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, %s)", (6, "2025-03-05", False))
                # 과목 4 (화요일, 목요일) - 3월 4일(화), 3월 6일(목)
                cursor.execute("INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, %s)", (7, "2025-03-04", False))
                cursor.execute("INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, %s)", (8, "2025-03-06", False))
                
                # 출석 정보 추가
                print("출석 데이터 삽입 중...")
                # 세션 1 (과목 1, 월요일) - 학생 1-5명 출석
                for student_id in range(1, 6):
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (1, student_id, "PRESENT"))
                # 세션 2 (과목 1, 수요일) - 학생 1-4명 출석, 학생 5명 지각
                for student_id in range(1, 5):
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (2, student_id, "PRESENT"))
                cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (2, 5, "LATE"))
                # 세션 3 (과목 2, 화요일) - 학생 3-6명 출석, 학생 7명 결석
                for student_id in range(3, 7):
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (3, student_id, "PRESENT"))
                cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (3, 7, "ABSENT"))
                # 세션 4 (과목 2, 목요일) - 학생 3-7명 모두 출석
                for student_id in range(3, 8):
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (4, student_id, "PRESENT"))
                # 세션 5 (과목 3, 월요일) - 학생 1-3, 9명 출석, 학생 4, 10명 지각
                for student_id in [1, 2, 3, 9]:
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (5, student_id, "PRESENT"))
                for student_id in [4, 10]:
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (5, student_id, "LATE"))
                # 세션 6 (과목 3, 수요일) - 학생 1-4, 9-10명 모두 출석
                for student_id in [1, 2, 3, 4, 9, 10]:
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (6, student_id, "PRESENT"))
                # 세션 7 (과목 4, 화요일) - 학생 5-8명 출석, 학생 9-10명 결석
                for student_id in range(5, 9):
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (7, student_id, "PRESENT"))
                for student_id in [9, 10]:
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (7, student_id, "ABSENT"))
                # 세션 8 (과목 4, 목요일) - 학생 5-10명 모두 출석
                for student_id in range(5, 11):
                    cursor.execute("INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)", (8, student_id, "PRESENT"))
                
                connection.commit()
                print("테스트 데이터 삽입 완료")
                return 0
    except Exception as e:
        print("테스트 데이터 삽입 과정 중 오류 발생: ", e)
        return 1

def add_student():
    try:
        name = input("이름: ")
        student_number = input("학번: ")
        major = input("전공: ")
        grade = int(input("학년: "))
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", (name, student_number, major, grade))
                connection.commit()
                print("학생 정보 추가 완료")
    except Exception as e:
        print("학생 정보 추가 중 오류 발생: ", e)

def add_professor():
    try:
        name = input("이름: ")
        major = input("전공: ")
        email = input("이메일: ")
        office_location = input("연구실 위치: ")
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("INSERT INTO professor (name, major, email, office_location) VALUES (%s, %s, %s, %s)", (name, major, email, office_location))
                connection.commit()
                print("교수 정보 추가 완료")
    except Exception as e:
        print("교수 정보 추가 중 오류 발생: ", e)

def add_subject():
    try:
        name = input("과목명: ")
        year = int(input("연도: "))
        semester = int(input("학기: "))
        professor_id_str = input("담당 교수 ID (없으면 Enter): ")
        professor_id = int(professor_id_str) if professor_id_str else None

        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE wcheck")
                if professor_id:
                    cursor.execute("INSERT INTO subject (name, subject_year, subject_semester, professor_id) VALUES (%s, %s, %s, %s)", (name, year, semester, professor_id))
                else:
                    cursor.execute("INSERT INTO subject (name, subject_year, subject_semester) VALUES (%s, %s, %s)", (name, year, semester))
                connection.commit()
                print("과목 정보 추가 완료")
    except Exception as e:
        print("과목 정보 추가 중 오류 발생: ", e)

def show_student():
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SELECT * FROM student")
                students = cursor.fetchall()
                if not students:
                    print("학생 정보가 없습니다.")
                    return
                for student in students:
                    print(f"ID: {student['student_id']}, 이름: {student['name']}, 학번: {student['student_number']}, 전공: {student['student_major']}, 학년: {student['student_grade']}")
    except Exception as e:
        print("학생 정보 조회 중 오류 발생: ", e)

def show_professor():
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SELECT * FROM professor")
                professors = cursor.fetchall()
                if not professors:
                    print("교수 정보가 없습니다.")
                    return
                for professor in professors:
                    print(f"ID: {professor['professor_id']}, 이름: {professor['name']}, 전공: {professor['major']}, 이메일: {professor['email']}, 연구실: {professor['office_location']}")
    except Exception as e:
        print("교수 정보 조회 중 오류 발생: ", e)

def show_subject():
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SELECT * FROM subject")
                subjects = cursor.fetchall()
                if not subjects:
                    print("과목 정보가 없습니다.")
                    return
                for subject in subjects:
                    print(f"ID: {subject['subject_id']}, 이름: {subject['name']}, 연도: {subject['subject_year']}, 학기: {subject['subject_semester']}, 교수 ID: {subject['professor_id']}")
    except Exception as e:
        print("과목 정보 조회 중 오류 발생: ", e)

def show_schedule():
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SELECT * FROM subject_schedule")
                schedules = cursor.fetchall()
                if not schedules:
                    print("시간표 정보가 없습니다.")
                    return
                for schedule in schedules:
                    print(f"ID: {schedule['schedule_id']}, 과목 ID: {schedule['subject_id']}, 요일: {schedule['day_of_week']}, 시작 시간: {schedule['start_time']}, 종료 시간: {schedule['end_time']}, 장소: {schedule['location']}")
    except Exception as e:
        print("시간표 정보 조회 중 오류 발생: ", e)

def show_session():
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SELECT * FROM class_session")
                sessions = cursor.fetchall()
                if not sessions:
                    print("수업 정보가 없습니다.")
                    return
                for session in sessions:
                    print(f"ID: {session['session_id']}, 시간표 ID: {session['schedule_id']}, 날짜: {session['class_date']}, 취소 여부: {'Y' if session['is_cancelled'] else 'N'}")
    except Exception as e:
        print("수업 정보 조회 중 오류 발생: ", e)

def show_checkin():
    try:
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SELECT * FROM checkin")
                checkins = cursor.fetchall()
                if not checkins:
                    print("출석 정보가 없습니다.")
                    return
                for checkin in checkins:
                    print(f"ID: {checkin['checkin_id']}, 수업 ID: {checkin['session_id']}, 학생 ID: {checkin['student_id']}, 출석 시간: {checkin['check_time']}, 상태: {checkin['status']}")
    except Exception as e:
        print("출석 정보 조회 중 오류 발생: ", e)

def show_all():
    show_student()
    print("-" * 20)
    show_professor()
    print("-" * 20)
    show_subject()
    print("-" * 20)
    show_schedule()
    print("-" * 20)
    show_session()
    print("-" * 20)
    show_checkin()

def delete_student():
    try:
        student_id = int(input("삭제할 학생의 ID를 입력하세요: "))
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
                connection.commit()
                if cursor.rowcount > 0:
                    print("학생 정보 삭제 완료")
                else:
                    print("해당 ID의 학생 정보가 없습니다.")
    except Exception as e:
        print("학생 정보 삭제 중 오류 발생: ", e)

def delete_professor():
    try:
        professor_id = int(input("삭제할 교수의 ID를 입력하세요: "))
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("DELETE FROM professor WHERE professor_id = %s", (professor_id,))
                connection.commit()
                if cursor.rowcount > 0:
                    print("교수 정보 삭제 완료")
                else:
                    print("해당 ID의 교수 정보가 없습니다.")
    except Exception as e:
        print("교수 정보 삭제 중 오류 발생: ", e)

def delete_subject():
    try:
        subject_id = int(input("삭제할 과목의 ID를 입력하세요: "))
        with connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("DELETE FROM subject WHERE subject_id = %s", (subject_id,))
                connection.commit()
                if cursor.rowcount > 0:
                    print("과목 정보 삭제 완료")
                else:
                    print("해당 ID의 과목 정보가 없습니다.")
    except Exception as e:
        print("과목 정보 삭제 중 오류 발생: ", e)

def update_student():
    try:
        student_id = int(input("수정할 학생의 ID를 입력하세요: "))
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
                student = cursor.fetchone()
                if not student:
                    print("해당 ID의 학생 정보가 없습니다.")
                    return

                print("수정할 정보를 입력하세요. (수정하지 않으려면 Enter)")
                name = input(f"이름 ({student['name']}): ") or student['name'] # or가 들어간 이유 : 입력을 하지 않으면 기존 값을 유지
                student_number = input(f"학번 ({student['student_number']}): ") or student['student_number']
                major = input(f"전공 ({student['student_major']}): ") or student['student_major']
                grade_str = input(f"학년 ({student['student_grade']}): ")
                grade = int(grade_str) if grade_str else student['student_grade']

                cursor.execute("UPDATE student SET name = %s, student_number = %s, student_major = %s, student_grade = %s WHERE student_id = %s",
                               (name, student_number, major, grade, student_id))
                connection.commit()
                print("학생 정보 수정 완료")
    except Exception as e:
        print("학생 정보 수정 중 오류 발생: ", e)

def update_professor():
    try:
        professor_id = int(input("수정할 교수의 ID를 입력하세요: "))
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SELECT * FROM professor WHERE professor_id = %s", (professor_id,))
                professor = cursor.fetchone()
                if not professor:
                    print("해당 ID의 교수 정보가 없습니다.")
                    return

                print("수정할 정보를 입력하세요. (수정하지 않으려면 Enter)")
                name = input(f"이름 ({professor['name']}): ") or professor['name']
                major = input(f"전공 ({professor['major']}): ") or professor['major']
                email = input(f"이메일 ({professor['email']}): ") or professor['email']
                office_location = input(f"연구실 위치 ({professor['office_location']}): ") or professor['office_location']

                cursor.execute("UPDATE professor SET name = %s, major = %s, email = %s, office_location = %s WHERE professor_id = %s",
                               (name, major, email, office_location, professor_id))
                connection.commit()
                print("교수 정보 수정 완료")
    except Exception as e:
        print("교수 정보 수정 중 오류 발생: ", e)

def update_subject():
    try:
        subject_id = int(input("수정할 과목의 ID를 입력하세요: "))
        with connect(**DB_CONFIG) as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("USE wcheck")
                cursor.execute("SELECT * FROM subject WHERE subject_id = %s", (subject_id,))
                subject = cursor.fetchone()
                if not subject:
                    print("해당 ID의 과목 정보가 없습니다.")
                    return

                print("수정할 정보를 입력하세요. (수정하지 않으려면 Enter)")
                name = input(f"과목명 ({subject['name']}): ") or subject['name']
                year_str = input(f"연도 ({subject['subject_year']}): ")
                year = int(year_str) if year_str else subject['subject_year']
                semester_str = input(f"학기 ({subject['subject_semester']}): ")
                semester = int(semester_str) if semester_str else subject['subject_semester']
                professor_id_str = input(f"담당 교수 ID ({subject['professor_id']}): ")
                professor_id = int(professor_id_str) if professor_id_str else subject['professor_id']

                cursor.execute("UPDATE subject SET name = %s, subject_year = %s, subject_semester = %s, professor_id = %s WHERE subject_id = %s",
                               (name, year, semester, professor_id, subject_id))
                connection.commit()
                print("과목 정보 수정 완료")
    except Exception as e:
        print("과목 정보 수정 중 오류 발생: ", e)

def main():
    print("WCHECK DB 관리 프로그램")
    while True:
        command = input("(도움말 : help) >")
        command_args = command.split(' ')
        if command_args[0] == 'help':
            print("help : 도움말 출력")
            print("reset : 데이터베이스 리셋")
            print("test : 데이터베이스 리셋 후 테스트 데이터 삽입")
            print("add (student | professor | subject) : 데이터 추가")
            print("delete (student | professor | subject) : 데이터 삭제")
            print("update (student | professor | subject) : 데이터 수정")
            print("show (student | professor | subject | schedule | session | checkin | all) : 데이터 조회")
            print("exit : 프로그램 종료")
        elif command_args[0] == 'reset':
            reset_database()
        elif command_args[0] == 'test':
            test_database()
        elif command_args[0] == 'add':
            if len(command_args) < 2:
                print("add (student | professor | subject)")
                continue
            if command_args[1] == 'student':
                add_student()
            elif command_args[1] == 'professor':
                add_professor()
            elif command_args[1] == 'subject':
                add_subject()
            else:
                print("올바르지 않은 명령어입니다. 도움말을 참고하세요.")
        elif command_args[0] == 'show':
            if len(command_args) < 2:
                print("show (student | professor | subject | schedule | session | checkin | all)")
                continue
            if command_args[1] == 'student':
                show_student()
            elif command_args[1] == 'professor':
                show_professor()
            elif command_args[1] == 'subject':
                show_subject()
            elif command_args[1] == 'schedule':
                show_schedule()
            elif command_args[1] == 'session':
                show_session()
            elif command_args[1] == 'checkin':
                show_checkin()
            elif command_args[1] == 'all':
                show_all()
            else:
                print("올바르지 않은 명령어입니다. 도움말을 참고하세요.")
        elif command_args[0] == 'delete':
            if len(command_args) < 2:
                print("delete (student | professor | subject)")
                continue
            if command_args[1] == 'student':
                delete_student()
            elif command_args[1] == 'professor':
                delete_professor()
            elif command_args[1] == 'subject':
                delete_subject()
            else:
                print("올바르지 않은 명령어입니다. 도움말을 참고하세요.")
        elif command_args[0] == 'update':
            if len(command_args) < 2:
                print("update (student | professor | subject)")
                continue
            if command_args[1] == 'student':
                update_student()
            elif command_args[1] == 'professor':
                update_professor()
            elif command_args[1] == 'subject':
                update_subject()
            else:
                print("올바르지 않은 명령어입니다. 도움말을 참고하세요.")
        elif command_args[0] == 'exit':
            break
        else:
            print("올바르지 않은 명령어입니다. 도움말을 참고하세요.")

if __name__ == "__main__":
    main()
        
        
       
from mysql.connector import connect
from ..config import DB_CONFIG

def login_user(student_number): # 로그인 함수
    try: 
        student_number = student_number.strip() # 앞뒤 공백 제거
        student_number = student_number.strip() # 앞뒤 공백 제거
        print(f"로그인 요청 받음 (repr): {repr(student_number)}") # 디버깅을 위한 출력
        with connect(**DB_CONFIG) as connection: # 데이터베이스 연결
            with connection.cursor(dictionary=True) as cursor: # 딕셔너리 형태로 결과를 가져오기 위해 dictionary=True 설정
                cursor.execute("SELECT student_number FROM student WHERE student_number = %s", (student_number,))
                result = cursor.fetchone() # 결과 반환
                if result:
                    db_student_number = result['student_number']
                    print(f"로그인 성공 (DB 학번 repr): {repr(db_student_number)}")
                else:
                    print(f"로그인 실패")
                return result is not None  # 결과가 있으면 True, 없으면 False 반환
    except Exception as e:
        print(f"Login error: {e}")
        return False # 오류 발생 시 False 반환
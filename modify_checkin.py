# modify_checkin.py

import mysql.connector
from config import DB_CONFIG

def print_help():
    """출결 수정 툴의 사용법을 안내합니다."""
    help_text = """
    ====================================================================
    ======= 출결 기록 수정 CLI (diskpart 스타일) =======
    ====================================================================
    - 사용법: [명령어] [인자...]
    - 예시: list 20250001
            modify 15 late

    [사용 가능한 명령어]
    - list <학번>: 해당 학생의 전체 출결 기록을 번호와 함께 조회합니다.
    - modify <출결ID> <상태>: 특정 출결 기록의 상태를 변경합니다.
      <출결ID>: 'list' 명령어로 확인한 출석 기록의 고유 ID(PK)
      <상태>: 'yes'(출석), 'late'(지각), 'no'(결석) 중 하나

    - help: 이 도움말을 다시 봅니다.
    - exit: 프로그램을 종료합니다.
    ====================================================================
    """
    print(help_text)

def list_checkins(student_id):
    """
    특정 학생의 모든 출결 기록을 DB에서 조회하여 출력합니다.
    [구현 로직 아이디어]
    1. DB에 연결합니다.
    2. Checkin 테이블과 Class_Session, Subject 테이블을 JOIN 합니다.
    3. WHERE 절을 이용해 특정 student_id의 기록만 가져옵니다.
    4. 결과를 보기 좋게 포맷팅하여 출력합니다. (예: ID, 과목명, 수업날짜, 현재상태)
    """
    print(f"'{student_id}' 학생의 출결 기록을 조회하는 로직을 구현해야 합니다.")
    print("예시 출력:")
    print(" ID | 과목명     | 수업 날짜    | 상태")
    print("----|------------|--------------|------")
    print(" 15 | 자료구조   | 2025-09-08   | yes")
    print(" 18 | 자료구조   | 2025-09-10   | late")
    pass

def modify_checkin(checkin_id_str, new_status):
    """
    특정 출결 기록의 상태를 수정합니다.
    [구현 로직 아이디어]
    1. new_status가 'yes', 'late', 'no' 중 하나인지 검증합니다.
    2. DB에 연결합니다.
    3. UPDATE 쿼리를 사용하여 Checkin 테이블의 is_safe 컬럼을 수정합니다.
       (WHERE id = {checkin_id})
    """
    print(f"'{checkin_id_str}'번 출결 기록의 상태를 '{new_status}'(으)로 변경하는 로직을 구현해야 합니다.")
    pass


def main():
    """메인 REPL(무한 루프)을 실행합니다."""
    print("출결 기록 수정 툴에 오신 것을 환영합니다. ('help' 입력)")
    
    while True:
        command_input = input("checkin-modifier> ").strip()
        if not command_input:
            continue

        parts = command_input.split()
        command = parts[0].lower()
        args = parts[1:]

        if command == 'exit':
            break
        
        if command == 'help':
            print_help()
            continue

        try:
            if command == 'list':
                if len(args) != 1:
                    print("오류: 'list' 명령어는 학번 1개가 필요합니다.")
                    continue
                list_checkins(args[0])

            elif command == 'modify':
                if len(args) != 2:
                    print("오류: 'modify' 명령어는 출결ID와 변경할 상태 2개가 필요합니다.")
                    continue
                modify_checkin(args[0], args[1])

            else:
                print(f"오류: 알 수 없는 명령어입니다: {command}")
        
        except Exception as e:
            print(f"!!! 오류 발생: {e}")

if __name__ == '__main__':
    main()
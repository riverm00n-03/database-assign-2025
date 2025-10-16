# admin_cli/admin.py

import sys
import os

# --- 경로 문제 해결 코드 (가장 위에 위치해야 합니다) ---
# 이 파일(admin.py)의 실제 경로를 찾고, 그 경로의 부모 폴더(admin_cli)의
# 또 그 부모 폴더(wcheck_project)를 파이썬의 모듈 검색 경로에 추가합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
# --- 여기까지 ---

# 이제 프로젝트 루트의 모듈들을 정상적으로 불러올 수 있습니다.
from config import DB_CONFIG
from commands import user_manage, course_manage, sys_manage


def print_help():
    """CLI 툴의 사용법을 안내하는 도움말을 출력합니다."""
    help_text = """
    ===========================================================================
    ======= WCheck 출석체크 시스템 관리자 CLI (대화형 모드) =======
    ===========================================================================
    [사용자 관리: user]
    - list_students
    - add_student <학번> <이름> <전공> <학년>
    - update_student <학번> <필드명> <새로운 값>
    - delete_student <학번>
    - (교수 관련 명령어들도 동일한 패턴)

    [과목 관리: course]
    - list_subjects
    - add_subject <과목명> <연도> <학기> <교수ID>
    - ... (과목/스케줄 CRUD)
    - generate_sessions <과목ID>

    [시스템 관리: system]
    - reset_database : 모든 테이블을 삭제하고 재생성합니다. (데이터 모두 삭제)
    - reset_database_test : DB 리셋 후 테스트용 더미 데이터를 채웁니다.

    - help: 이 도움말을 다시 봅니다.
    - exit: 프로그램을 종료합니다.
    ===========================================================================
    """
    print(help_text)


def main():
    """CLI 툴의 메인 로직을 실행하는 REPL입니다."""
    print("WCheck 관리자 CLI에 오신 것을 환영합니다. ('help' 입력)")

    while True:
        try:
            command_input = input("wcheck-admin> ").strip()
        except KeyboardInterrupt: # Ctrl+C 입력 시 종료
            print("\nCLI 툴을 종료합니다.")
            break
            
        if not command_input:
            continue

        parts = command_input.split()
        command_group = parts[0].lower()

        if command_group in ['exit', 'quit']:
            print("CLI 툴을 종료합니다.")
            break
        
        if command_group == 'help':
            print_help()
            continue

        # 'system reset_database' 와 같은 복합 명령어 우선 처리
        if command_group == 'system':
            full_command = " ".join(parts[1:])
            if full_command == 'reset_database':
                sys_manage.reset_database()
            elif full_command == 'reset_database_test':
                sys_manage.reset_database_test()
            else:
                print(f"오류: 알 수 없는 system 명령어입니다. 'reset_database' 또는 'reset_database_test'를 사용하세요.")
            continue

        if len(parts) < 2:
            print("오류: 세부 명령어를 입력해주세요. (예: user list_students)")
            continue

        sub_command = parts[1].lower()
        args = parts[2:]

        try:
            if command_group == 'user':
                # 여기에 user_manage의 함수들을 호출하는 분기 로직을 구현하세요.
                # 예: if sub_command == 'add_student': user_manage.add_student(*args)
                print(f"-> 'user {sub_command}' 명령어 실행 로직 구현 필요. 인자: {args}")

            elif command_group == 'course':
                # 여기에 course_manage의 함수들을 호출하는 분기 로직을 구현하세요.
                print(f"-> 'course {sub_command}' 명령어 실행 로직 구현 필요. 인자: {args}")

            else:
                print(f"오류: 알 수 없는 명령어 그룹입니다: {command_group}")

        except Exception as e:
            print(f"!!! 명령어 실행 중 오류가 발생했습니다: {e}")


if __name__ == '__main__':
    main()
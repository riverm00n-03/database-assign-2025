#!/usr/bin/env python3
"""
일일 자동 결석 처리 스크립트
23시 59분에 실행하여 그날 출석 데이터가 없는 경우 자동으로 결석 처리

사용법:
    python scripts/auto_absent_daily.py
    
또는 cron으로 실행:
    59 23 * * * /usr/bin/python3 /path/to/scripts/auto_absent_daily.py
"""
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.auto_absent import run_daily_auto_absent


if __name__ == "__main__":
    try:
        processed_count, absent_count = run_daily_auto_absent()
        print(f"처리 완료: {processed_count}개 세션, {absent_count}명 결석 처리")
        sys.exit(0)
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)


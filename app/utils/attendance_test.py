from datetime import datetime, timedelta

# 원하는 기준 시간
FAKE_NOW = datetime(2025, 9, 8, 9, 0, 0)  # 원하는 날짜/시간 입력

def now():
    """프로젝트 전체에서 현재 시간을 가져올 때 사용"""
    return FAKE_NOW

def today():
    return FAKE_NOW.date()

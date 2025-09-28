"""
데이터베이스 테이블의 구조를 SQL CREATE 구문으로 정의함.
이곳의 SQL 쿼리문들은 core.py의 init_tables 함수에서 실행됨.
"""

# 사용자 계정 정보와 프로필 정보를 통합하여 저장하는 테이블임.
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    
    -- 프로필 정보를 통합:
    nickname VARCHAR(50) DEFAULT NULL,
    context_info TEXT DEFAULT NULL,  /* 사용자의 성격, 선호 등을 AI에게 전달할 필드 */

    is_banned TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# AI 캐릭터(스토리)의 정보를 저장하는 테이블임.
CREATE_STORIES_TABLE = """
CREATE TABLE IF NOT EXISTS stories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    prompt TEXT NOT NULL,
    category VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
)
"""

# 사용자와 스토리 간의 채팅방 정보를 저장하는 테이블임.
CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    story_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- last_updated_at 컬럼을 제거하여 단순화함.
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
)
"""

# 실제 채팅 메시지 기록을 저장하는 테이블임.
CREATE_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    sender VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
)
"""

# 위에 정의된 모든 CREATE 쿼리들을 리스트로 묶어둠.
# user_profiles 테이블 쿼리는 제거됨.
CREATE_TABLE_QUERIES = [
    CREATE_USERS_TABLE,
    CREATE_STORIES_TABLE,
    CREATE_SESSIONS_TABLE,
    CREATE_HISTORY_TABLE,
]
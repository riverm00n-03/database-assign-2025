# 사용자 정보 (user) 테이블
# 로그인, 계정 관리 등 사용자 인증의 기반이 됩니다.
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    is_banned TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0: normal, 1: banned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# 스토리 정보 (stories) 테이블
# 각 스토리의 정체성(프롬프트, 제목, 카테고리 등)을 정의합니다.
# personal : 사람과 대화하는 듯한 1대1 채팅 / simulation : RPG/시뮬레이션 등등 텍스트 게임 / productivity : 작사, 코딩 등등 생산성에 맞춘 느낌.
CREATE_STORIES_TABLE = """
CREATE TABLE IF NOT EXISTS stories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    prompt TEXT NOT NULL,
    category VARCHAR(20) NOT NULL COMMENT "'personal', 'simulation', or 'productivity'",
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
)
"""

# 채팅방(세션) 정보를 저장할 session 테이블.
# 어떤 유저가 어떤 스토리와 대화하는지를 연결하며, 대화하는 유저 외의 다른 유저가 채팅방을 보는 것을 막기 위한 식별기 역할도 할 겁니다.
CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    story_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
)
"""

#  채팅 기록을 저장할 history 테이블
# 각 세션(채팅방) 에서 오고 간 대화 내용을 순서대로 저장합니다.
CREATE_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    sender VARCHAR(10) NOT NULL COMMENT "'user' or 'ai'",
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
)
"""

# 위에 정의된 모든 CREATE 쿼리들을 리스트로 묶어둠
CREATE_TABLE_QUERIES = [
    CREATE_USERS_TABLE,
    CREATE_STORIES_TABLE,
    CREATE_SESSIONS_TABLE,
    CREATE_HISTORY_TABLE,
]

# 위 리스트는 core.py에서 사용될 겁니다.


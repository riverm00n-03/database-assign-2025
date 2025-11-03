-- 0. 이미 데이터베이스가 구축된 경우, 데이터베이스를 건드리지 않음.
-- 1. 데이터베이스 생성 (이미 존재하지 않는 경우에만)
CREATE DATABASE IF NOT EXISTS wcheck
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 2. 생성한 데이터베이스 사용
USE wcheck;
-- 3. 학생 정보 테이블
CREATE TABLE IF NOT EXISTS student (
    student_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '학생 이름',
    student_number VARCHAR(50) NOT NULL UNIQUE COMMENT '학번',
    student_major VARCHAR(100) COMMENT '전공 (ERD 참조)',
    student_grade INT UNSIGNED COMMENT '학년 (ERD 참조)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '가입일'
) COMMENT '학생 정보';

-- 4. 교수 정보 테이블 (신규 추가!)
CREATE TABLE IF NOT EXISTS professor (
    professor_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '교수 이름',
    major VARCHAR(100) COMMENT '전공 (ERD 참조)',
    email VARCHAR(100) UNIQUE COMMENT '이메일 (확장성)',
    office_location VARCHAR(100) COMMENT '연구실 위치 (확장성)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '등록일'
) COMMENT '교수 정보';

-- 5. 과목 정보 테이블 (수정됨)
CREATE TABLE IF NOT EXISTS subject (
    subject_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    professor_id INT UNSIGNED DEFAULT NULL COMMENT '교수 외래키', -- 'professor_name' 대신 추가됨
    name VARCHAR(255) NOT NULL COMMENT '과목명',
    subject_year INT UNSIGNED COMMENT '개설 연도 (ERD 참조)',
    subject_semester INT UNSIGNED COMMENT '개설 학기 (ERD 참조)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '과목 개설일',

    FOREIGN KEY (professor_id) REFERENCES professor(professor_id)
        ON DELETE SET NULL
        --   -> (설명) 만약 'professor' 테이블(부모)에서 1번 교수가 삭제(퇴직 등)되더라도,
        --      'subject' 테이블(자식)의 과목은 삭제되지 않고, 'professor_id'만 NULL로 변경됩니다.
        --      (CASCADE로 설정하면 교수가 삭제될 때 과목까지 연쇄 삭제되므로, SET NULL이 더 안전합니다)
) COMMENT '과목 정보';

-- 6. 과목 시간표 테이블 (수업 규칙)
CREATE TABLE IF NOT EXISTS subject_schedule (
    schedule_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    subject_id INT UNSIGNED NOT NULL COMMENT '과목 외래키',
    day_of_week ENUM('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN') NOT NULL COMMENT '수업 요일',
    start_time TIME NOT NULL COMMENT '수업 시작 시간',
    end_time TIME NOT NULL COMMENT '수업 종료 시간',
    location VARCHAR(100) COMMENT '강의실',
    
    FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
        ON DELETE CASCADE
        --   -> (설명) 과목이 삭제되면(부모), 관련 시간표(자식)도 모두 자동 삭제됩니다.
) COMMENT '과목별 시간표 (수업 규칙 템플릿)';

-- 7. 학생-과목 수강 매핑 테이블 (ERD의 'enrollment')
CREATE TABLE IF NOT EXISTS enrollment (
    student_id INT UNSIGNED NOT NULL COMMENT '학생 외래키',
    subject_id INT UNSIGNED NOT NULL COMMENT '과목 외래키',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '수강 신청일',
    
    PRIMARY KEY (student_id, subject_id),
    
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
        ON DELETE CASCADE
) COMMENT '학생-과목 수강 매핑 (M:N 관계)';

-- 8. 개별 수업일 테이블 (신규 추가! ERD의 'class_session')
CREATE TABLE IF NOT EXISTS class_session (
    session_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT UNSIGNED NOT NULL COMMENT '시간표 외래키',
    class_date DATE NOT NULL COMMENT '실제 수업 날짜',
    is_cancelled BOOLEAN DEFAULT FALSE COMMENT '휴강 여부 (ERD 참조)',
    
    UNIQUE KEY (schedule_id, class_date), -- 동일한 시간표(월 10시)가 같은 날짜(10/27)에 중복 생성되는 것 방지
    
    FOREIGN KEY (schedule_id) REFERENCES subject_schedule(schedule_id)
        ON DELETE CASCADE
        --   -> (설명) '월 10시 수업'이라는 규칙(부모)이 삭제되면,
        --      관련된 모든 실제 수업(10/20, 10/27, 11/3...) 기록(자식)도 자동 삭제됩니다.
) COMMENT '개별 실제 수업일 (출석 대상)';

-- 9. 출석 기록 테이블 (수정됨)
CREATE TABLE IF NOT EXISTS checkin (
    checkin_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id INT UNSIGNED NOT NULL COMMENT '개별 수업 외래키', -- 'subject_id' 대신 추가됨
    student_id INT UNSIGNED NOT NULL COMMENT '학생 외래키',
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '출석 시간',
    status ENUM('PRESENT', 'LATE', 'ABSENT') DEFAULT 'PRESENT' COMMENT '출석 상태',
    
    UNIQUE KEY (session_id, student_id), -- 학생은 한 수업에 한 번만 출석 가능
    
    FOREIGN KEY (session_id) REFERENCES class_session(session_id)
        ON DELETE CASCADE,
        --   -> 10월 27일 수업(부모) 기록이 삭제되면, 해당 수업의 모든 출석 기록(자식)도 자동 삭제됩니다.
        
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE
) COMMENT '출석 기록';
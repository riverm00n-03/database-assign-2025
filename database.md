# 데이터베이스 구조 개요

본 문서는 `db/create.sql`을 기준으로 한 WCheck 시스템의 데이터베이스 스키마와 동작 시나리오를 정리합니다. 모든 설명은 MySQL 8.x 호환을 전제로 합니다.

## 테이블 요약

| 테이블 | 목적 | 주요 컬럼 | 비고 |
| --- | --- | --- | --- |
| `student` | 학생 기본 정보 | `student_id`, `name`, `student_number`, `student_major`, `student_grade`, `created_at` | 학번(`student_number`) UNIQUE |
| `professor` | 교수 기본 정보 | `professor_id`, `name`, `major`, `email`, `office_location`, `created_at` | 이메일 UNIQUE |
| `subject` | 과목 정보 | `subject_id`, `professor_id`, `name`, `subject_year`, `subject_semester`, `created_at` | 교수 삭제 시 `professor_id` → `NULL` |
| `subject_schedule` | 과목별 반복 수업 슬롯 | `schedule_id`, `subject_id`, `day_of_week`, `start_time`, `end_time`, `location` | 과목 삭제 시 함께 삭제 |
| `enrollment` | 학생-과목 수강 매핑 | `student_id`, `subject_id`, `registered_at` | 복합 PK(`student_id`, `subject_id`) |
| `class_session` | 실제 주차별 수업 인스턴스 | `session_id`, `schedule_id`, `class_date`, `is_cancelled` | `(schedule_id, class_date)` UNIQUE |
| `checkin` | 학생 출결 기록 | `checkin_id`, `session_id`, `student_id`, `check_time`, `status` | `(session_id, student_id)` UNIQUE |

## 테이블별 상세 설명

### student (학생 정보 테이블)

**목적 및 필요성:**
- 학생의 기본 정보를 저장하는 핵심 테이블입니다.
- 출석 시스템의 주체인 학생을 식별하고 관리하기 위해 필요합니다.
- 학번을 통한 고유 식별과 함께 전공, 학년 등 추가 정보를 제공합니다.

**컬럼 설명:**
- `student_id` : 학번과 별개로 사용하는 내부 식별자 (PK, AUTO_INCREMENT).
- `name` : 학생 실명.
- `student_number` : 학교에서 부여하는 고유 학번, 중복 불가 (UNIQUE).
- `student_major` : 전공명. 미정 시 `NULL` 허용.
- `student_grade` : 학년(정수). 편입/휴학자는 별도 비즈니스 규칙으로 관리.
- `created_at` : 가입 시각.

**관계:**
- `enrollment` 테이블과 1:N 관계 (한 학생이 여러 과목 수강)
- `checkin` 테이블과 1:N 관계 (한 학생이 여러 출석 기록 보유)
- 학생 삭제 시 `enrollment`, `checkin`에서도 CASCADE로 기록 제거

**핵심 시나리오:**
- 신규 학생 등록 시 INSERT 후 학번 중복 여부를 UNIQUE 제약으로 보장.
- 학생 정보 수정 시 UPDATE를 통해 전공/학년 변경.
- 학생 삭제 시 `enrollment`, `checkin`에서도 CASCADE로 기록 제거.

### professor (교수 정보 테이블)

**목적 및 필요성:**
- 교수의 기본 정보를 저장하는 테이블입니다.
- 과목에 담당 교수를 배정하고, 교수별 과목 목록을 조회하기 위해 필요합니다.
- 교수 퇴직 시에도 과목 정보는 유지되도록 설계되었습니다.

**컬럼 설명:**
- `professor_id` : 교수 식별자 (PK, AUTO_INCREMENT).
- `name` : 교수 실명.
- `major` : 담당 학과 또는 연구분야.
- `email` : 업무용 이메일, UNIQUE.
- `office_location` : 연구실 위치.
- `created_at` : 등록 시각.

**관계:**
- `subject` 테이블과 1:N 관계 (한 교수가 여러 과목 담당)
- 교수 삭제 시 `subject.professor_id`가 `NULL`로 변환되어 과목은 유지 (ON DELETE SET NULL)

**핵심 시나리오:**
- 신규 교수 채용 시 INSERT로 등록.
- 교수 퇴직으로 삭제하면 `subject.professor_id`가 `NULL`로 변환되어 과목은 유지.
- 교수 정보 변경 시 과목 목록 조회 등에서 갱신된 데이터 사용.

### subject (과목 정보 테이블)

**목적 및 필요성:**
- 개설된 과목의 정보를 저장하는 테이블입니다.
- 학기별, 연도별 과목 관리와 출석 시스템의 중심이 되는 테이블입니다.
- 교수 배정, 학기 정보 등을 통해 체계적인 과목 관리를 가능하게 합니다.

**컬럼 설명:**
- `subject_id` : 과목 식별자 (PK, AUTO_INCREMENT).
- `professor_id` : 담당 교수 FK. 미지정 과목은 `NULL`.
- `name` : 과목명.
- `subject_year` : 개설 연도.
- `subject_semester` : 학기(1=봄, 2=가을 등 기관 규칙 준수).
- `created_at` : 과목 생성 시각.

**관계:**
- `professor` 테이블과 N:1 관계 (여러 과목이 한 교수에게 배정 가능)
- `subject_schedule` 테이블과 1:N 관계 (한 과목이 여러 시간표 슬롯 보유)
- `enrollment` 테이블과 1:N 관계 (한 과목에 여러 학생 수강)
- 과목 삭제 시 FK CASCADE에 따라 시간표/세션/출석이 함께 삭제됨

**핵심 시나리오:**
- 학과에서 과목 추가 시 INSERT.
- 담당 교수 교체 시 UPDATE로 `professor_id` 변경.
- 과목 폐지 시 FK CASCADE에 따라 시간표/세션/출석이 함께 삭제됨.

### subject_schedule (과목별 시간표 테이블)

**목적 및 필요성:**
- 과목의 주간 반복 수업 패턴을 정의하는 테이블입니다.
- "월요일 10시", "수요일 14시" 같은 반복되는 수업 시간을 템플릿으로 저장합니다.
- 이 템플릿을 기반으로 실제 수업 세션(`class_session`)을 생성할 수 있습니다.
- 주차당 수업 수를 계산하는 데 사용됩니다 (총 수업 수 = 주차 수 × 주차당 수업 수).

**컬럼 설명:**
- `schedule_id` : 반복 수업 슬롯 식별자 (PK, AUTO_INCREMENT).
- `subject_id` : 해당 과목 FK.
- `day_of_week` : 요일 ENUM (`MON`~`SUN`).
- `start_time` : 수업 시작 시각.
- `end_time` : 수업 종료 시각.
- `location` : 강의실 정보.

**관계:**
- `subject` 테이블과 N:1 관계 (한 과목이 여러 시간표 슬롯 보유)
- `class_session` 테이블과 1:N 관계 (한 시간표 슬롯에서 여러 실제 수업 세션 생성)
- 과목 삭제 시 CASCADE로 모든 슬롯 자동 삭제

**핵심 시나리오:**
- 학기 개설 시 과목별 요일·시간 정보를 INSERT.
- 수업 시간 변경 시 UPDATE로 조정, 이후 생성되는 세션에 반영.
- 과목 삭제 시 CASCADE로 모든 슬롯 자동 삭제.

### enrollment (학생-과목 수강 매핑 테이블)

**목적 및 필요성:**
- 학생과 과목의 다대다(M:N) 관계를 표현하는 매핑 테이블입니다.
- 한 학생이 여러 과목을 수강하고, 한 과목에 여러 학생이 수강할 수 있으므로 중간 테이블이 필요합니다.
- 수강 신청 시점을 기록하여 수강 이력 관리가 가능합니다.

**컬럼 설명:**
- `student_id` : 수강생 FK.
- `subject_id` : 수강 과목 FK.
- `registered_at` : 신청 시각 (디폴트 현재 시각).

**관계:**
- `student` 테이블과 N:1 관계 (여러 수강 기록이 한 학생에게 속함)
- `subject` 테이블과 N:1 관계 (여러 수강 기록이 한 과목에 속함)
- 복합 PRIMARY KEY (`student_id`, `subject_id`)로 중복 수강 방지
- 학생 또는 과목 삭제 시 CASCADE로 수강 기록 삭제

**핵심 시나리오:**
- 수강 신청 확정 시 INSERT.
- 수강 취소 시 DELETE. 이후 해당 학생의 출석 데이터는 남아있을 수 있으므로 백엔드 로직으로 처리.
- 복합 PK 덕분에 중복 신청 방지.

### class_session (개별 수업일 테이블)

**목적 및 필요성:**
- 실제로 진행되는 주차별 수업 인스턴스를 저장하는 테이블입니다.
- `subject_schedule`의 템플릿을 기반으로 실제 날짜별 수업을 생성합니다.
- 휴강 처리를 통해 출석 집계에서 제외할 수 있습니다.
- 출석률 계산 시 "정보가 있는 수업 수"를 판단하는 데 사용됩니다.

**컬럼 설명:**
- `session_id` : 주차별 실제 수업 식별자 (PK, AUTO_INCREMENT).
- `schedule_id` : 어떤 반복 슬롯에서 파생됐는지 FK.
- `class_date` : 실제 수업 날짜.
- `is_cancelled` : 휴강 여부 (TRUE 시 출석률 계산에 포함되지만 출석 의무는 없음).

**관계:**
- `subject_schedule` 테이블과 N:1 관계 (한 시간표 슬롯에서 여러 실제 수업 세션 생성)
- `checkin` 테이블과 1:N 관계 (한 수업 세션에 여러 학생의 출석 기록)
- 시간표 슬롯 삭제 시 CASCADE로 모든 세션 자동 삭제
- UNIQUE 제약 (`schedule_id`, `class_date`)으로 동일 날짜 중복 생성 방지

**핵심 시나리오:**
- 학기 시작 시 모든 주차를 미리 INSERT.
- 휴강 확정 시 `is_cancelled = TRUE`로 UPDATE.
- 보강 수업은 동일 `schedule_id`로 날짜를 추가 INSERT.

### checkin (출석 기록 테이블)

**목적 및 필요성:**
- 학생의 실제 출석 기록을 저장하는 테이블입니다.
- 출석, 지각, 결석 상태를 기록하여 출석률 계산의 기초 데이터가 됩니다.
- 출석 시간을 기록하여 지각 판정 등에 활용할 수 있습니다.

**컬럼 설명:**
- `checkin_id` : 출석 기록 식별자 (PK, AUTO_INCREMENT).
- `session_id` : 해당 수업 FK.
- `student_id` : 학생 FK.
- `check_time` : 출석 체크 기록 시각.
- `status` : `PRESENT`, `LATE`, `ABSENT` 중 하나.

**관계:**
- `class_session` 테이블과 N:1 관계 (여러 출석 기록이 한 수업 세션에 속함)
- `student` 테이블과 N:1 관계 (여러 출석 기록이 한 학생에게 속함)
- UNIQUE 제약 (`session_id`, `student_id`)으로 한 학생이 한 수업에 중복 출석 방지
- 수업 세션 또는 학생 삭제 시 CASCADE로 출석 기록 자동 삭제

**핵심 시나리오:**
- 학생 출석 스캔 시 INSERT 혹은 UPSERT로 기록.
- 지각/결석 수동 조정 시 `status` UPDATE.
- 학생 혹은 수업 삭제 시 CASCADE로 관련 출석 자동 삭제.

## 관계 및 제약 요약

### 외래키 관계

1. **subject → professor**
   - `subject.professor_id` → `professor.professor_id`
   - `ON DELETE SET NULL`: 교수 삭제 시 과목의 교수 배정만 해제되고 과목은 유지

2. **subject_schedule → subject**
   - `subject_schedule.subject_id` → `subject.subject_id`
   - `ON DELETE CASCADE`: 과목 삭제 시 관련 시간표도 함께 삭제

3. **enrollment → student**
   - `enrollment.student_id` → `student.student_id`
   - `ON DELETE CASCADE`: 학생 삭제 시 수강 기록도 함께 삭제

4. **enrollment → subject**
   - `enrollment.subject_id` → `subject.subject_id`
   - `ON DELETE CASCADE`: 과목 삭제 시 수강 기록도 함께 삭제

5. **class_session → subject_schedule**
   - `class_session.schedule_id` → `subject_schedule.schedule_id`
   - `ON DELETE CASCADE`: 시간표 슬롯 삭제 시 관련 세션도 함께 삭제

6. **checkin → class_session**
   - `checkin.session_id` → `class_session.session_id`
   - `ON DELETE CASCADE`: 수업 세션 삭제 시 출석 기록도 함께 삭제

7. **checkin → student**
   - `checkin.student_id` → `student.student_id`
   - `ON DELETE CASCADE`: 학생 삭제 시 출석 기록도 함께 삭제

### 데이터 흐름

```
student ──┐
          ├──→ enrollment ──→ subject ──→ subject_schedule ──→ class_session ──→ checkin
          └───────────────────────────────────────────────────────────────────────┘
```

관계 관점에서는 `student` ↔ `subject`가 `enrollment`로 연결되고, `subject` ↔ `subject_schedule` ↔ `class_session` ↔ `checkin`으로 이어지는 출결 흐름을 구성합니다.

## 출석률 계산 로직

### 총 수업 수 계산
- **공식**: 주차 수 × 주차당 수업 수
- **주차 수**: 학기 시작일부터 종료일까지 계산 (최대 16주)
- **주차당 수업 수**: `subject_schedule` 테이블에서 해당 과목의 스케줄 개수
- 출석 정보(`checkin`)가 없어도 계산 가능

### 출석률 계산
- **공식**: (출석 완료된 수 + 휴강 수) / (전체 수업 수 - 정보가 없는 수업 수)
- **출석 완료된 수**: `PRESENT` + `LATE` (지각도 출석으로 간주)
- **휴강 수**: `class_session.is_cancelled = TRUE`인 수업 수
- **전체 수업 수**: 주차 수 × 주차당 수업 수
- **정보가 없는 수업 수**: 아직 생성되지 않은 수업 세션 (전체 수업 수 - 실제 생성된 세션 수)

## 생성/조회 플로우 예시

아래는 DB 초기 설정 직후, 학생·과목·스케줄·수강을 단계적으로 등록하고 검증하는 절차입니다.

### 1) DB 초기 설정

- 방식 A: 스크립트 실행 (권장)
  - `db/create.sql` 전체를 실행합니다. 데이터베이스(`wcheck`) 생성부터 모든 테이블이 준비됩니다.

- 방식 B: 수동 생성 (요약)
```sql
CREATE DATABASE IF NOT EXISTS wcheck
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE wcheck;
-- 이후 create.sql의 테이블 생성문들을 순차 실행
```

### 2) 학생 추가

```sql
-- 학생 등록
INSERT INTO student (name, student_number, student_major, student_grade)
VALUES ('홍길동', '202512345', 'Computer Science', 2);

-- 등록한 학생의 ID 조회 (학번으로 조회)
SELECT student_id
FROM student
WHERE student_number = '202512345';
```

설명:
- 학번(`student_number`)은 UNIQUE라서 중복 시 에러가 발생합니다.
- 애플리케이션에서는 INSERT 직후 반환 ID를 받거나, 학번으로 재조회하여 `student_id`를 확보합니다.

### 3) 과목 및 (선택) 교수 추가

```sql
-- (선택) 교수 등록
INSERT INTO professor (name, major, email, office_location)
VALUES ('김교수', 'Computer Science', 'prof.kim@example.edu', 'B-402');

-- 교수 ID 조회 (이메일로 조회)
SELECT professor_id FROM professor WHERE email = 'prof.kim@example.edu';

-- 과목 등록 (교수 배정 포함)
INSERT INTO subject (name, subject_year, subject_semester, professor_id)
VALUES ('데이터베이스', 2025, 1, /* 위에서 조회한 */ 1);

-- 과목 ID 조회 (LAST_INSERT_ID() 사용 예)
SELECT LAST_INSERT_ID() AS subject_id;
```

설명:
- 교수 배정이 없으면 `professor_id`를 생략하거나 `NULL`로 넣을 수 있습니다.
- 과목명은 UNIQUE가 아니므로, 신뢰 가능한 식별을 위해 `LAST_INSERT_ID()`나 별도 비즈니스 키(연도·학기 조합)를 사용하세요.

### 4) 스케줄(주간 반복 슬롯) 추가

```sql
-- 월요일 3교시 (예: 10:00~10:50)
INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location)
VALUES (/* subject_id */ 101, 'MON', '10:00:00', '10:50:00', 'E-201');

-- 수요일 5~6교시 (예: 14:00~15:50)
INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location)
VALUES (101, 'WED', '14:00:00', '15:50:00', 'E-201');

-- 방금 추가한 스케줄 확인
SELECT schedule_id, day_of_week, start_time, end_time, location
FROM subject_schedule
WHERE subject_id = 101
ORDER BY FIELD(day_of_week,'MON','TUE','WED','THU','FRI','SAT','SUN'), start_time;
```

설명:
- 한 과목이 여러 요일·교시를 가질 수 있으므로 슬롯별로 한 행씩 INSERT 합니다.
- 과목이 삭제되면 해당 과목의 스케줄도 CASCADE로 삭제됩니다.

### 5) 수강(학생-과목 매핑) 추가

```sql
-- 수강 등록 (중복 방지: 복합 PK)
INSERT INTO enrollment (student_id, subject_id)
VALUES (/* student_id */ 1, /* subject_id */ 101);

-- (선택) 멱등 호출을 원하면
INSERT IGNORE INTO enrollment (student_id, subject_id)
VALUES (1, 101);

-- 수강 확인
SELECT e.student_id, s.name AS subject_name, e.registered_at
FROM enrollment e
JOIN subject s ON s.subject_id = e.subject_id
WHERE e.student_id = 1;
```

설명:
- 복합 PK(`student_id`,`subject_id`)로 동일 학생의 중복 수강 신청이 차단됩니다.
- `INSERT IGNORE`를 사용하면 중복 시 에러 대신 무시되어 멱등성이 확보됩니다.

### 6) (선택) 학기 주차별 수업 인스턴스 생성

```sql
-- 스케줄로부터 특정 날짜의 수업 세션 생성
INSERT INTO class_session (schedule_id, class_date)
VALUES (/* schedule_id */ 15, '2025-03-05');

-- 생성 확인
SELECT session_id, schedule_id, class_date, is_cancelled
FROM class_session
WHERE schedule_id = 15
ORDER BY class_date;
```

설명:
- 실제 출석 집계를 위해 학기 시작 시점에 전체 주차를 일괄 생성하는 것을 권장합니다.
- 휴강은 `is_cancelled = TRUE`로 표시하거나, 보강은 새로운 날짜 행을 추가합니다.

### 7) (참고) 학생의 주차별 출석 확인

```sql
SELECT
    cs.class_date,
    ss.day_of_week,
    ss.start_time,
    ss.end_time,
    IF(cs.is_cancelled, 'CANCELLED', COALESCE(c.status, 'ABSENT')) AS attendance_status,
    c.check_time
FROM enrollment e
JOIN subject s ON s.subject_id = e.subject_id
JOIN subject_schedule ss ON ss.subject_id = s.subject_id
JOIN class_session cs ON cs.schedule_id = ss.schedule_id
LEFT JOIN checkin c ON c.session_id = cs.session_id AND c.student_id = e.student_id
WHERE e.student_id = 1
  AND e.subject_id = 101
ORDER BY cs.class_date;
```

설명:
- 휴강(`is_cancelled=TRUE`)은 출석 여부와 무관하게 `CANCELLED`로 표기합니다.
- 출석 미기록(LEFT JOIN NULL)은 `ABSENT`로 간주해 요약에 반영할 수 있습니다.

## 운영 상 유의 사항

- `class_session`은 학기 시작 전 일괄 생성하거나, 수업 주차 직전에 배치 작업으로 생성하는 패턴이 일반적입니다.
- 휴강/보강 처리 시 `class_session.is_cancelled`를 업데이트하거나 새로운 세션을 추가하고, 관련 출석(`checkin`)을 정정해야 합니다.
- FK 성능 확보를 위해 `subject_schedule.subject_id`, `enrollment.student_id`, `enrollment.subject_id`, `class_session.schedule_id`, `checkin.session_id`, `checkin.student_id` 등에 인덱스를 명시적으로 추가하는 것을 권장합니다.
- 출석 상태 값이 늘어날 가능성이 있다면 `checkin.status`를 ENUM 대신 코드 테이블로 분리하는 방식을 검토하세요.

이 문서는 운영자 및 개발자가 동일한 DB 구조 이해를 바탕으로 기능을 구현하거나 데이터를 점검할 때 참고용으로 활용할 수 있습니다.

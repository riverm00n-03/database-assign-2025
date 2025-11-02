# WCHECK
## 1. 환경 설정

### `.env` 파일 생성

프로젝트 루트 디렉토리에 `.env` 파일을 생성하여 데이터베이스 연결 정보를 설정해야 합니다. `config.py` 파일은 이 `.env` 파일에서 환경 변수를 읽어옵니다.

`.env` 파일의 예시:

```
# .env 파일
# 이 파일은 애플리케이션의 환경 변수를 정의합니다.
# 민감한 정보는 여기에 직접 작성하지 않고, 배포 환경에서는 별도의 보안 메커니즘을 사용해야 합니다.

# 데이터베이스 설정
DB_HOST=db
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=wcheck

# Flask 애플리케이션 시크릿 키 (필요시 주석 해제 후 사용)
# SECRET_KEY=your_flask_secret_key_입력
```

*   `DB_PASSWORD`: MySQL `root` 사용자의 비밀번호 입력
*   `SECRET_KEY`: Flask 애플리케이션의 세션 관리를 위한 시크릿 키를 입력하는 부분.

## 2. Docker Compose를 사용하여 실행

프로젝트를 Docker Compose를 사용하여 빌드하고 실행할 수 있습니다.

1.  **이미지 빌드 및 컨테이너 실행**:
    프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다.

    ```bash
    docker-compose up --build
    ```

    *   `--build` 옵션은 변경 사항이 있을 경우 Docker 이미지를 다시 빌드합니다.
    *   이 명령은 `db` 서비스와 `web` 서비스를 시작합니다. `db` 서비스는 MySQL 데이터베이스를, `web` 서비스는 Flask 애플리케이션을 실행합니다.

2.  **백그라운드에서 실행**:
    컨테이너를 백그라운드에서 실행하려면 `-d` 옵션을 추가합니다.

    ```bash
    docker-compose up -d --build
    ```

3.  **컨테이너 중지**:
    실행 중인 컨테이너를 중지하려면 다음 명령어를 사용합니다.

    ```bash
    docker-compose down
    ```

## 3. 애플리케이션 접속

Docker Compose가 성공적으로 실행되면, 웹 브라우저에서 다음 주소로 Flask 애플리케이션에 접속할 수 있습니다:

```
http://localhost:5000
```

## 4. 데이터베이스 초기화

`db/create.sql` 파일은 데이터베이스 스키마를 정의하고 초기 데이터를 삽입합니다. `docker-compose up` 명령을 실행할 때 `db` 서비스가 시작되면서 create.sql이 실행됩니다.
(이미 데이터베이스가 구축되어 있는 경우에는 create.sql 내부 쿼리문의 조건에 따라 DB에 수정히 가해지지 않습니다.)

## 5. 관리자 CLI 사용

`admin.py` 파일은 데이터베이스를 관리하기 위한 파이썬 스크립트입니다.
docker-compose exec web python admin.py 이런 명령어로 꼭 실행해야 합니다. (그냥 admin.py를 실행할 경우, docker의 데이터베이스를 건드리는 것이 아닌 로컬 데이터베이스 서버에서 실행되는 문제가 있음.)

이 명령을 통해 데이터베이스 리셋, 학생/교수/과목 추가/조회/수정/삭제 등의 작업을 수행할 수 있습니다.
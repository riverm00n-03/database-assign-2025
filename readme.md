
-   **Backend**: `Python 3.12`, `FastAPI`
-   **Database**: `MySQL 8.0`
-   **AI**: `Google Gemini API`
-   **Server**: `Uvicorn`
-   **Containerization**: `Docker`, `Docker Compose`
-   **Dependencies**: `PyMySQL`, `python-dotenv`, `Werkzeug`

 **Docker 컨테이너 실행**
    아래 명령어를 실행하면 필요한 모든 라이브러리가 설치되고, 웹 서버와 데이터베이스 컨테이너가 실행됩니다.
    ```bash
    docker-compose up --build
    ```
    > 서버가 정상적으로 실행되면, 터미널에 `Uvicorn running on http://0.0.0.0:8000` 메시지가 출력됩니다.

4.  **서버 종료**
    서버를 종료하려면 터미널에서 `Ctrl + C`를 누른 후, 아래 명령어를 실행하여 컨테이너를 완전히 중지 및 제거합니다.
    ```bash
    docker-compose down
    ```

<br>

## 사용법

서버가 실행 중인 상태에서, 웹 브라우저로 [http://localhost:8000/docs](http://localhost:8000/docs)에 접속하면 FastAPI가 제공하는 자동 API 문서를 확인할 수 있습니다. 이 페이지에서 각 API를 확인하고 직접 테스트해볼 수 있습니다.

### 주요 API 엔드포인트
-   `GET /`: 서버 동작 확인
-   `GET /init-db`: 프로젝트에 필요한 모든 데이터베이스 테이블을 생성합니다. (최초 1회 실행)
-   `GET /check-db`: 생성된 테이블들의 스키마 구조를 JSON 형태로 확인합니다.
-   `POST /users/register`: 새로운 사용자를 등록합니다. 아래 형식의 JSON 데이터를 Body에 담아 요청해야 합니다.
    ```json
    {
      "username": "testuser",
      "password": "password123",
      "email": "test@example.com"
    }
    ```

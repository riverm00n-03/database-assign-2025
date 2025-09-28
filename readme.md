# 실행하는 방법
docker, docker-desktop(선택) 설치

프로젝트 폴더에서
docker-compose up --build로 빌드 후 실행

# 웹 브라우저에서 기능 확인

Hello World: http://localhost:5000/ 접속

"Hello World"가 보이면 성공

DB 테이블 생성: http://localhost:5000/init-db 접속

{"status": "success", "message": "..."} 메시지가 보이면 테이블 생성 성공

DB 구조 확인: http://localhost:5000/check-db 접속

JSON 형태로 users와 chat_history 테이블의 구조(컬럼 이름, 타입 등)가 자세하게 보이면 성공

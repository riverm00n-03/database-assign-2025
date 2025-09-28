from app import create_app

# 플라스크 앱 생성함.
app = create_app()

if __name__ == '__main__':
    # host='0.0.0.0'로 설정해야 Docker 컨테이너 외부에서 접속 가능
    app.run(host='0.0.0.0', debug=True)

# Python 실행기와 필요한 Linux 파일이 있는 기반 이미지
FROM python:3.12-slim

# 로그를 바로 출력하고, 프로그램이 사용할 기본 설정을 지정한다.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SERVICE_HOST=0.0.0.0 \
    SERVICE_PORT=8000 \
    SERVICE_NAME=meeting-runtime \
    APP_VERSION=v1

# 프로그램을 실행할 일반 사용자를 만든다.
RUN useradd --create-home --uid 10001 app
# 이미지 안의 작업 위치를 정하고 소스를 복사한다.
WORKDIR /app
COPY --chown=app:app app.py .
# 이후 컨테이너의 프로그램은 app 사용자로 실행한다.
USER app

# 사용 포트를 설명한다. 실제 호스트 연결은 docker run의 -p로 정한다.
EXPOSE 8000
# 컨테이너를 시작할 때 실행할 기본 명령
CMD ["python", "app.py"]
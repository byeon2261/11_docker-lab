# 서비스 배포 및 자동화 운영



## 2.Dockerfile과 이미지 빌드

| 파일 | 역할 |
| --- | --- |
| `app.py` | 요청을 받고 실행 정보를 응답하는 작은 HTTP 서버 |
| `Dockerfile` | 어떤 파일과 실행 환경으로 이미지를 만들지 적는 파일 |
| `.dockerignore` | 이미지 빌드에 보낼 파일에서 제외할 대상을 적는 파일 |

#### 기본 네 지시어

작업 폴더에 `Dockerfile`을 만들고 다음 네 줄을 작성한다. 먼저 실행에 필요한 기본 구조를 확인하고, 같은 파일에 설정을 더해 아래의 전체 구성으로 확장한다. 최종적으로는 전체 구성을 저장한 **Dockerfile 하나**를 사용한다.

| 작성할 줄 | 정하는 것 | 실제로 준비되는 내용 |
| --- | --- | --- |
| `FROM python:3.12-slim` | 새 이미지의 출발점 | Python 실행기와 필요한 Linux 파일이 들어 있는 기반 이미지에서 시작 |
| `WORKDIR /app` | 이미지 안의 작업 위치 | `/app`이 없으면 만들고, 이후 상대 경로와 컨테이너 시작 위치의 기준으로 사용 |
| `COPY app.py .` | 이미지에 넣을 프로그램 파일 | 내 PC의 빌드 대상 폴더에 있는 `app.py`를 이미지의 `/app/app.py`로 복사 |
| `CMD ["python", "app.py"]` | 컨테이너 시작 시 실행할 기본 명령 | `/app`에서 `python app.py` 실행. 빌드할 때는 이 명령으로 서버를 시작하지 않음 |

```sh
docker build -t meeting-runtime:v1 .
```
```sh
[+] Building 15.8s (9/9) FINISHED                                                                                    docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                 0.1s
 => => transferring dockerfile: 888B                                                                                                 0.0s
 => [internal] load metadata for docker.io/library/python:3.12-slim                                                                  2.3s
 => [internal] load .dockerignore                                                                                                    0.1s
 => => transferring context: 306B                                                                                                    0.0s
 => [1/4] FROM docker.io/library/python:3.12-slim@sha256:191083cdf6c7bda8c76158983163ead5d5cf7b77cf3033e805bb0f5296f51b4b            4.6s
 => => resolve docker.io/library/python:3.12-slim@sha256:191083cdf6c7bda8c76158983163ead5d5cf7b77cf3033e805bb0f5296f51b4b            0.1s
 => => ....
 => => extracting sha256:286d8c291daa64125703b22c3d009462bcae0b630eaa16ad5b934502c4917233                                            0.1s
 => [internal] load build context                                                                                                    0.2s
 => => transferring context: 2.50kB                                                                                                  0.0s
 => [2/4] RUN useradd --create-home --uid 10001 app                                                                                  3.3s
 => [3/4] WORKDIR /app                                                                                                               0.4s
 => [4/4] COPY --chown=app:app app.py .                                                                                              0.5s
 => exporting to image                                                                                                               3.9s
 => ....                                                                              0.0s
 => => unpacking to docker.io/library/meeting-runtime:v1  
```

```sh
docker image ls meeting-runtime
                                                                                                                     i Info →   U  In Use
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
meeting-runtime:v1   7f9ed346fcb3        177MB         43.3MB 
```

```sh
docker run -d --name meeting-runtime -p 8080:8000 meeting-runtime:v1
419686042c0fdea9883cc5f34f385f7f2a7b502829515a434b7e8de3984c4990
```

image에

## 3.컨테이너 격리와 파일 수명
...
### 이미지 계층과 파일 변경

방금의 결과를 파일 저장 위치로 설명해 보자. **계층**은 파일 구성을 나눈 층이다. 이미지의 파일 계층은 실행 중에 바꾸지 않는 원본이고, 컨테이너를 만들면 그 위에 이 컨테이너만의 **쓰기 계층**이 생긴다.


## 4.컨테이너 실행 오류 진단

### 실패 위치와 확인 순서
명령 하나를 외우는 대신 “어디까지 성공했는가”를 기준으로 다음 관찰을 고른다.

| 증상 | 먼저 확인할 위치 | 이번에 사용한 근거 |
| --- | --- | --- |
| Docker Server에 연결하지 못함 | Engine 실행과 클라이언트 연결 | `docker version`, 컨텍스트 |
| 빌드가 파일을 못 찾음 | 작업 위치·빌드 컨텍스트·제외 규칙 | Dockerfile의 COPY와 마지막 `.` |
| 컨테이너가 즉시 종료됨 | 시작 명령과 실제 오류 | `docker ps -a`, `docker logs` |
| 컨테이너는 실행 중인데 접속 실패 | 게시 포트와 서버 수신 포트·주소 | `docker port`, 실제 수신 로그 |
| HTTP 404 | 요청 경로 | 서버가 응답한 상태 코드와 `path` |
| 두 번째 실행에서 포트 점유 | 호스트 게시 포트 | 실행 중인 컨테이너와 포트 목록 |
| 재생성 후 임시 파일 소실 | 파일의 저장 경계 | 기존 쓰기 계층과 새 컨테이너의 구별 |

실제 일정 서비스에서는 여기에 웹→API, API→Supabase·모델·도구 경계가 추가된다. 지금 확인한 프로세스·포트 문제를 업무 검증 실패와 혼동하지 않는 것이 먼저다.

### 소스 변경과 이미지 교체

```bash
docker build -t meeting-runtime:v2 . #이미지 생성
docker run -d --name meeting-updated -p 8084:8000 -e APP_VERSION=v2 meeting-runtime:v2 #컨테이너 생성
docker inspect --format "{{.Config.Image}}" meeting-updated
```
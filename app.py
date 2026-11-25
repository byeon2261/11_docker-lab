"""HTTP 응답으로 컨테이너의 실제 실행 환경을 관찰한다."""

import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class RuntimeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """실행 정보와 프로세스 생존 여부를 HTTP로 반환한다."""
        # URL에서 경로를 읽고, 실행 공간의 호스트명과 프로세스 번호를 확인한다.
        path = urlsplit(self.path).path
        identity = {"hostname": socket.gethostname(), "pid": os.getpid()}
        if path == "/":
            self.send_json(200, {
                "service_name": os.getenv("SERVICE_NAME", "meeting-runtime"),
                "app_version": os.getenv("APP_VERSION", "v1"),
                **identity,
                "listening_host": self.server.server_address[0],
                "listening_port": self.server.server_address[1],
                "runtime_note": "v2 source", # 코드가 바꼈을 때의 테스트를 위한 속성값 
            })
        elif path == "/health":
            self.send_json(200, {"status": "alive", **identity})
        else:
            self.send_json(404, {"error": "not_found", "path": path})

    def send_json(self, status, value):
        """상태 코드와 UTF-8 JSON 본문을 함께 전송한다."""
        # Python 데이터를 JSON으로 바꾸고, 네트워크로 보낼 바이트를 만든다.
        body = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    """환경변수의 주소에서 HTTP 서버를 실행한다."""
    # 실행할 때 전달한 설정을 읽는다. 없으면 두 번째 인자의 기본값을 쓴다.
    host = os.getenv("SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SERVICE_PORT", "8000"))
    # 지정한 주소·포트에서 요청을 받고, 각 요청을 RuntimeHandler로 처리한다.
    server = ThreadingHTTPServer((host, port), RuntimeHandler)
    print(f"Listening on {host}:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


# 이 파일을 직접 실행하면 서버를 시작한다.
if __name__ == "__main__":
    main()
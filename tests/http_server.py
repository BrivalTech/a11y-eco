"""A tiny local HTTP server for tests: no test ever goes on the internet."""

from __future__ import annotations

import contextlib
import threading
import time
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REQUESTS: list[dict[str, str]] = []


@dataclass(frozen=True)
class Route:
    """The answer of the server for one path."""

    body: bytes = b""
    status: int = 200
    headers: Mapping[str, str] = field(default_factory=dict)
    delay: float = 0.0
    """Seconds to wait before answering, to test timeouts."""


@contextlib.contextmanager
def serve(routes: Mapping[str, Route]) -> Iterator[str]:
    """Serve the routes on a free local port and yield the base URL.

    Unknown paths answer 404. The last request headers are kept in ``REQUESTS``.
    """

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            REQUESTS.append(dict(self.headers.items()))
            route = routes.get(self.path, Route(status=404))
            time.sleep(route.delay)
            self.send_response(route.status)
            for name, value in route.headers.items():
                self.send_header(name, value)
            self.send_header("Content-Length", str(len(route.body)))
            self.end_headers()
            with contextlib.suppress(OSError):  # the client may have given up
                self.wfile.write(route.body)

        def log_message(self, format: str, *args: object) -> None:
            """Keep the test output quiet."""

    REQUESTS.clear()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{httpd.server_port}"
    finally:
        httpd.shutdown()
        httpd.server_close()

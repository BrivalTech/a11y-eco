import contextlib
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from a11y_eco.loader import LoadError, detect_encoding, load


@pytest.mark.parametrize(
    ("data", "declared", "expected"),
    [
        pytest.param(b"\xef\xbb\xbf<p>", None, "utf-8-sig", id="utf-8-bom"),
        pytest.param(b"\xff\xfe<\x00p\x00", None, "utf-16", id="utf-16-bom"),
        pytest.param(b"\xef\xbb\xbf<p>", "iso-8859-1", "utf-8-sig", id="bom-beats-header"),
        pytest.param(b"<p>", "UTF-8", "utf-8", id="header"),
        pytest.param(b'<meta charset="utf-8">', "windows-1252", "cp1252", id="header-beats-meta"),
        pytest.param(b'<meta charset="windows-1252">', None, "cp1252", id="meta-charset"),
        pytest.param(
            b'<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-15">',
            None,
            "iso8859-15",
            id="meta-http-equiv",
        ),
        pytest.param(b"<p>", "iso-8859-1", "cp1252", id="latin-1-read-as-windows-1252"),
        pytest.param(b"<p>", "not-an-encoding", "utf-8", id="unknown-label-ignored"),
        pytest.param(b"<p>", None, "utf-8", id="default"),
    ],
)
def test_detect_encoding(data: bytes, declared: str | None, expected: str) -> None:
    assert detect_encoding(data, declared) == expected


def test_meta_charset_is_only_searched_at_the_start() -> None:
    late_meta = b" " * 2000 + b'<meta charset="windows-1252">'

    assert detect_encoding(late_meta) == "utf-8"


def test_loads_a_utf8_file(tmp_path: Path) -> None:
    page = tmp_path / "page.html"
    page.write_bytes("<p>Café</p>".encode())

    source = load(str(page))

    assert source.text == "<p>Café</p>"
    assert source.size == 12  # "é" takes two bytes in UTF-8
    assert source.encoding == "utf-8"
    assert source.location == str(page)


def test_decodes_windows_1252_characters_missing_from_latin_1(tmp_path: Path) -> None:
    page = tmp_path / "page.html"
    page.write_bytes(b'<meta charset="iso-8859-1"><p>\x80 \x9c</p>')

    assert load(str(page)).text.endswith("<p>€ œ</p>")


def test_invalid_bytes_are_replaced_instead_of_failing(tmp_path: Path) -> None:
    page = tmp_path / "page.html"
    page.write_bytes(b"<p>\xff</p>")

    assert load(str(page)).text == "<p>\ufffd</p>"


def test_missing_file_is_a_load_error(tmp_path: Path) -> None:
    with pytest.raises(LoadError, match="cannot read"):
        load(str(tmp_path / "missing.html"))


def test_load_error_carries_its_message_key_and_values(tmp_path: Path) -> None:
    missing = tmp_path / "missing.html"

    with pytest.raises(LoadError) as exc_info:
        load(str(missing))

    assert exc_info.value.key == "load.unreadable"
    assert exc_info.value.params["path"] == missing


def test_directory_is_a_load_error(tmp_path: Path) -> None:
    with pytest.raises(LoadError, match="cannot read"):
        load(str(tmp_path))


def test_file_larger_than_limit_is_refused(tmp_path: Path) -> None:
    page = tmp_path / "page.html"
    page.write_bytes(b"x" * 11)

    assert load(str(page), max_bytes=11).size == 11
    with pytest.raises(LoadError, match="limit"):
        load(str(page), max_bytes=10)


ROUTES: dict[str, tuple[int, dict[str, str], bytes]] = {
    "/page": (200, {"Content-Type": "text/html; charset=utf-8"}, "<p>Café</p>".encode()),
    "/latin": (200, {"Content-Type": "text/html; charset=iso-8859-1"}, b"<p>Caf\xe9</p>"),
    "/moved": (301, {"Location": "/page"}, b""),
    "/missing": (404, {"Content-Type": "text/html"}, b"<h1>Not found</h1>"),
    "/image": (200, {"Content-Type": "image/png"}, b"\x89PNG"),
}
SLOW_RESPONSE_DELAY = 0.5


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/slow":
            time.sleep(SLOW_RESPONSE_DELAY)
        status, headers, body = ROUTES.get(self.path, ROUTES["/page"])
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        with contextlib.suppress(OSError):  # the client may have given up (timeout test)
            self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        """Keep the test output quiet."""


@pytest.fixture(scope="module")
def server() -> Iterator[str]:
    """Serve ROUTES on a free local port and yield its base URL."""
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def test_loads_a_page_from_a_url(server: str) -> None:
    source = load(f"{server}/page")

    assert source.text == "<p>Café</p>"
    assert source.encoding == "utf-8"


def test_uses_the_charset_sent_by_the_server(server: str) -> None:
    assert load(f"{server}/latin").text == "<p>Café</p>"


def test_follows_redirects_and_reports_final_url(server: str) -> None:
    assert load(f"{server}/moved").location == f"{server}/page"


def test_http_error_status_is_a_load_error(server: str) -> None:
    with pytest.raises(LoadError, match="404"):
        load(f"{server}/missing")


def test_non_html_content_is_refused(server: str) -> None:
    with pytest.raises(LoadError, match="image/png"):
        load(f"{server}/image")


def test_slow_server_is_a_load_error(server: str) -> None:
    with pytest.raises(LoadError, match="did not answer"):
        load(f"{server}/slow", timeout=0.1)


def test_unreachable_host_is_a_load_error() -> None:
    with pytest.raises(LoadError, match="cannot reach"):
        load("http://127.0.0.1:9/", timeout=2)

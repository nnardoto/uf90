from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import sys

import pytest

from uf90.lsp import (
    JsonRpcProtocolError,
    read_message,
    resolve_fortls,
    run_proxy,
    write_message,
)


def frame(message: dict) -> bytes:
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    return f"Content-Length: {len(body)}\r\n\r\n".encode() + body


def test_reads_multiple_messages_and_clean_eof():
    first = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    second = {"jsonrpc": "2.0", "method": "exit", "params": {}}
    stream = BytesIO(frame(first) + frame(second))

    assert read_message(stream) == first
    assert read_message(stream) == second
    assert read_message(stream) is None


def test_content_length_counts_utf8_bytes():
    message = {"jsonrpc": "2.0", "method": "test", "params": {"name": "α"}}
    stream = BytesIO()

    write_message(stream, message)

    raw_headers, raw_body = stream.getvalue().split(b"\r\n\r\n", 1)
    assert raw_headers == f"Content-Length: {len(raw_body)}".encode()
    assert read_message(BytesIO(stream.getvalue())) == message


@pytest.mark.parametrize(
    "payload",
    [
        b"Content-Type: application/vscode-jsonrpc\r\n\r\n{}",
        b"Content-Length: nope\r\n\r\n{}",
        b"Content-Length: 3\r\n\r\n{}",
        b"Content-Length: 1\r\n\r\n[",
    ],
)
def test_rejects_invalid_frames(payload: bytes):
    with pytest.raises(JsonRpcProtocolError):
        read_message(BytesIO(payload))


def test_resolves_explicit_or_path_fortls():
    assert resolve_fortls({"UF90_FORTLS_PATH": "/tools/fortls"}) == "/tools/fortls"
    assert resolve_fortls({}, which=lambda name: f"/path/{name}") == "/path/fortls"


def test_rejects_missing_fortls_and_proxy_recursion():
    with pytest.raises(FileNotFoundError, match="fortls não encontrado"):
        resolve_fortls({}, which=lambda name: None)
    with pytest.raises(RuntimeError, match="executável fortls real"):
        resolve_fortls(
            {"UF90_FORTLS_PATH": "/tools/uf90-ls"}, launcher="/other/uf90-ls"
        )


def test_proxy_forwards_messages_through_deterministic_server(tmp_path: Path):
    server = tmp_path / "fake_server.py"
    server.write_text(
        """
import json
import sys

line = sys.stdin.buffer.readline()
length = int(line.decode().split(':', 1)[1])
assert sys.stdin.buffer.readline() == b'\\r\\n'
message = json.loads(sys.stdin.buffer.read(length))
response = {'jsonrpc': '2.0', 'id': message['id'], 'result': {'forwarded': True}}
body = json.dumps(response, separators=(',', ':')).encode()
sys.stdout.buffer.write(f'Content-Length: {len(body)}\\r\\n\\r\\n'.encode() + body)
sys.stdout.buffer.flush()
""".lstrip(),
        encoding="utf-8",
    )
    request = {"jsonrpc": "2.0", "id": 7, "method": "initialize", "params": {}}
    output = BytesIO()

    return_code = run_proxy(
        [str(server)],
        stdin=BytesIO(frame(request)),
        stdout=output,
        env={"UF90_FORTLS_PATH": sys.executable},
    )

    assert return_code == 0
    assert read_message(BytesIO(output.getvalue())) == {
        "jsonrpc": "2.0",
        "id": 7,
        "result": {"forwarded": True},
    }


def test_proxy_preserves_server_exit_status(tmp_path: Path):
    server = tmp_path / "failed_server.py"
    server.write_text("raise SystemExit(7)\n", encoding="utf-8")

    assert run_proxy(
        [str(server)],
        stdin=BytesIO(frame({"jsonrpc": "2.0", "id": 1, "method": "initialize"})),
        stdout=BytesIO(),
        env={"UF90_FORTLS_PATH": sys.executable},
    ) == 7

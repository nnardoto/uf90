from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
from typing import Any, BinaryIO


MAX_MESSAGE_BYTES = 64 * 1024 * 1024


class JsonRpcProtocolError(ValueError):
    """An invalid JSON-RPC/LSP frame was received."""


class FortlsNotFoundError(FileNotFoundError):
    """The underlying fortls executable could not be located."""


def _read_exact(stream: BinaryIO, length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = length
    while remaining:
        chunk = stream.read(remaining)
        if not chunk:
            received = length - remaining
            raise JsonRpcProtocolError(
                f"unexpected EOF in message body ({received}/{length} bytes)"
            )
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_message(stream: BinaryIO) -> dict[str, Any] | None:
    """Read one Content-Length framed LSP message.

    ``None`` represents a clean EOF before the next header. Message bodies are
    decoded as UTF-8, while Content-Length is always measured in bytes.
    """

    headers: dict[str, str] = {}
    while True:
        raw_line = stream.readline()
        if raw_line == b"":
            if not headers:
                return None
            raise JsonRpcProtocolError("unexpected EOF in message headers")
        if raw_line in {b"\r\n", b"\n"}:
            break
        if not raw_line.endswith(b"\n"):
            raise JsonRpcProtocolError("unterminated message header")

        try:
            line = raw_line.decode("ascii").strip("\r\n")
        except UnicodeDecodeError as exc:
            raise JsonRpcProtocolError("message headers must be ASCII") from exc
        if ":" not in line:
            raise JsonRpcProtocolError(f"malformed message header: {line!r}")
        name, value = line.split(":", 1)
        normalized_name = name.strip().lower()
        if normalized_name in headers:
            raise JsonRpcProtocolError(f"duplicate message header: {name.strip()}")
        headers[normalized_name] = value.strip()

    raw_length = headers.get("content-length")
    if raw_length is None:
        raise JsonRpcProtocolError("missing Content-Length header")
    try:
        length = int(raw_length)
    except ValueError as exc:
        raise JsonRpcProtocolError("invalid Content-Length header") from exc
    if length < 0 or length > MAX_MESSAGE_BYTES:
        raise JsonRpcProtocolError(f"Content-Length outside allowed range: {length}")

    body = _read_exact(stream, length)
    try:
        message = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JsonRpcProtocolError("invalid UTF-8 JSON message body") from exc
    if not isinstance(message, dict):
        raise JsonRpcProtocolError("LSP message body must be a JSON object")
    return message


def write_message(stream: BinaryIO, message: Mapping[str, Any]) -> None:
    body = json.dumps(
        message, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    stream.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
    stream.write(body)
    stream.flush()


def forward_messages(
    source: BinaryIO,
    destination: BinaryIO,
    transform: Callable[[dict[str, Any]], Mapping[str, Any]] | None = None,
) -> None:
    while True:
        message = read_message(source)
        if message is None:
            return
        write_message(destination, transform(message) if transform else message)


def resolve_fortls(
    env: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] = shutil.which,
    launcher: str | None = None,
) -> str:
    current_env = os.environ if env is None else env
    executable = current_env.get("UF90_FORTLS_PATH") or which("fortls")
    if not executable:
        raise FortlsNotFoundError(
            "fortls não encontrado; instale-o ou defina UF90_FORTLS_PATH"
        )

    launcher_path = Path(sys.argv[0] if launcher is None else launcher)
    executable_path = Path(executable)
    try:
        same_executable = executable_path.resolve() == launcher_path.resolve()
    except OSError:
        same_executable = False
    if same_executable or executable_path.name.lower() in {"uf90-ls", "uf90-ls.exe"}:
        raise RuntimeError(
            "UF90_FORTLS_PATH aponta para uf90-ls; selecione o executável fortls real"
        )
    return executable


def run_proxy(
    args: Sequence[str] = (),
    *,
    stdin: BinaryIO | None = None,
    stdout: BinaryIO | None = None,
    env: Mapping[str, str] | None = None,
    client_transform: Callable[[dict[str, Any]], Mapping[str, Any]] | None = None,
    server_transform: Callable[[dict[str, Any]], Mapping[str, Any]] | None = None,
) -> int:
    client_input = sys.stdin.buffer if stdin is None else stdin
    client_output = sys.stdout.buffer if stdout is None else stdout
    fortls = resolve_fortls(env=env)

    process = subprocess.Popen(
        [fortls, *args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert process.stdin is not None
    assert process.stdout is not None

    client_errors: list[Exception] = []

    def client_to_server() -> None:
        try:
            forward_messages(client_input, process.stdin, client_transform)
        except Exception as exc:
            client_errors.append(exc)
        finally:
            try:
                process.stdin.close()
            except BrokenPipeError as exc:
                if not client_errors:
                    client_errors.append(exc)

    input_thread = threading.Thread(
        target=client_to_server,
        name="uf90-ls-client-to-fortls",
        daemon=True,
    )
    input_thread.start()

    try:
        forward_messages(process.stdout, client_output, server_transform)
    except Exception:
        if process.poll() is None:
            process.terminate()
        process.wait()
        raise

    return_code = process.wait()
    input_thread.join(timeout=1)
    if client_errors:
        if return_code and all(
            isinstance(error, BrokenPipeError) for error in client_errors
        ):
            return return_code
        raise client_errors[0]
    return return_code


def main(argv: Sequence[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        from .lsp_session import LspSession

        session = LspSession()
        return run_proxy(
            args,
            client_transform=session.client_to_server,
            server_transform=session.server_to_client,
        )
    except FortlsNotFoundError as exc:
        print(f"uf90-ls: {exc}", file=sys.stderr)
        return 127
    except (JsonRpcProtocolError, RuntimeError, BrokenPipeError, OSError) as exc:
        print(f"uf90-ls: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

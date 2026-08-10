from __future__ import annotations

import os
from pathlib import Path
from queue import Empty, Queue
import shutil
import subprocess
import sys
import threading
from typing import Any

import pytest

from uf90.lsp import read_message, write_message


def _fortls_executable() -> str | None:
    executable = shutil.which("fortls")
    if executable:
        return executable
    sibling = Path(sys.executable).with_name(
        "fortls.exe" if sys.platform == "win32" else "fortls"
    )
    return str(sibling) if sibling.is_file() else None


class LspClient:
    def __init__(self, root: Path, fortls: str) -> None:
        env = os.environ.copy()
        env["UF90_FORTLS_PATH"] = fortls
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uf90.lsp", "--disable_autoupdate"],
            cwd=root,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        self._messages: Queue[dict[str, Any] | BaseException | None] = Queue()
        self.notifications: list[dict[str, Any]] = []
        self._reader = threading.Thread(target=self._read_messages, daemon=True)
        self._reader.start()

    def _read_messages(self) -> None:
        assert self.process.stdout is not None
        try:
            while True:
                message = read_message(self.process.stdout)
                self._messages.put(message)
                if message is None:
                    return
        except BaseException as exc:
            self._messages.put(exc)

    def send(self, message: dict[str, Any]) -> None:
        assert self.process.stdin is not None
        write_message(self.process.stdin, message)

    def response(self, request_id: int, timeout: float = 15) -> dict[str, Any]:
        while True:
            try:
                message = self._messages.get(timeout=timeout)
            except Empty as exc:
                raise AssertionError(
                    f"timed out waiting for LSP response {request_id}"
                ) from exc
            if isinstance(message, BaseException):
                raise message
            if message is None:
                raise AssertionError(
                    f"uf90-ls exited before responding to request {request_id}: "
                    f"{self.stderr()}"
                )
            if message.get("id") == request_id:
                return message
            self.notifications.append(message)

    def shutdown(self) -> None:
        if self.process.poll() is not None:
            raise AssertionError(f"uf90-ls exited early: {self.stderr()}")
        self.send({"jsonrpc": "2.0", "id": 900, "method": "shutdown", "params": None})
        response = self.response(900)
        assert response.get("result") is None
        self.send({"jsonrpc": "2.0", "method": "exit", "params": {}})
        assert self.process.stdin is not None
        self.process.stdin.close()
        assert self.process.wait(timeout=10) == 0, self.stderr()

    def close(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=10)

    def stderr(self) -> str:
        if self.process.stderr is None or self.process.poll() is None:
            return ""
        return self.process.stderr.read().decode("utf-8", errors="replace")


def _request(request_id: int, method: str, params: dict[str, Any]) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params,
    }


@pytest.mark.integration
def test_oscillator_navigation_hover_and_unsaved_changes(tmp_path: Path):
    fortls = _fortls_executable()
    if fortls is None:
        pytest.skip("fortls is not installed")

    repository = Path(__file__).parents[2]
    root = tmp_path / "oscillator"
    shutil.copytree(repository / "examples" / "06_oscillator", root)
    main = root / "app" / "main.f90u"
    generated = main.with_suffix(".f90")
    client = LspClient(root, fortls)

    try:
        client.send(
            _request(
                1,
                "initialize",
                {
                    "processId": None,
                    "rootUri": root.as_uri(),
                    "workspaceFolders": [{"uri": root.as_uri(), "name": root.name}],
                    "capabilities": {
                        "general": {"positionEncodings": ["utf-16"]},
                        "textDocument": {
                            "publishDiagnostics": {"relatedInformation": True}
                        },
                    },
                },
            )
        )
        initialized = client.response(1)
        assert initialized["result"]["capabilities"]["textDocumentSync"][
            "change"
        ] == 1
        client.send({"jsonrpc": "2.0", "method": "initialized", "params": {}})

        source_text = main.read_text(encoding="utf-8")
        client.send(
            {
                "jsonrpc": "2.0",
                "method": "textDocument/didOpen",
                "params": {
                    "textDocument": {
                        "uri": main.as_uri(),
                        "languageId": "FortranFreeForm",
                        "version": 1,
                        "text": source_text,
                    }
                },
            }
        )

        position = {"line": 9, "character": 9}
        params = {"textDocument": {"uri": main.as_uri()}, "position": position}
        client.send(_request(2, "textDocument/definition", params))
        definition = client.response(2)["result"]
        locations = definition if isinstance(definition, list) else [definition]
        target_uri = locations[0].get("uri") or locations[0].get("targetUri")
        assert target_uri.endswith("/src/oscillator.f90u")
        target_range = locations[0].get("range") or locations[0].get(
            "targetSelectionRange"
        )
        assert target_range["start"] == {"line": 7, "character": 20}
        assert target_range["end"] == {"line": 7, "character": 21}

        client.send(_request(3, "textDocument/hover", params))
        hover = client.response(3)["result"]
        assert "ω" in str(hover)
        assert "uc_omega" not in str(hover)

        reference_params = {
            **params,
            "context": {"includeDeclaration": True},
        }
        client.send(_request(4, "textDocument/references", reference_params))
        references = client.response(4)["result"]
        assert references
        assert all(location["uri"].endswith(".f90u") for location in references)

        synced_generated = generated.read_text(encoding="utf-8")
        added_line = "  print *, system%ω\n"
        changed_text = source_text.replace(
            "end program oscillator_example", f"{added_line}end program oscillator_example"
        )
        added_line_number = changed_text[: changed_text.index(added_line)].count("\n")
        client.send(
            {
                "jsonrpc": "2.0",
                "method": "textDocument/didChange",
                "params": {
                    "textDocument": {"uri": main.as_uri(), "version": 2},
                    "contentChanges": [{"text": changed_text}],
                },
            }
        )
        assert generated.read_text(encoding="utf-8") == synced_generated

        client.send(
            _request(
                5,
                "textDocument/definition",
                {
                    "textDocument": {"uri": main.as_uri()},
                    "position": {"line": added_line_number, "character": 18},
                },
            )
        )
        unsaved_definition = client.response(5)["result"]
        unsaved_locations = (
            unsaved_definition
            if isinstance(unsaved_definition, list)
            else [unsaved_definition]
        )
        assert unsaved_locations
        unsaved_target = unsaved_locations[0].get("uri") or unsaved_locations[0].get(
            "targetUri"
        )
        assert unsaved_target.endswith("/src/oscillator.f90u")

        completion_line = "  print *, \\alp\n"
        completion_text = changed_text.replace(
            "end program oscillator_example",
            f"{completion_line}end program oscillator_example",
        )
        completion_line_number = completion_text[
            : completion_text.index(completion_line)
        ].count("\n")
        client.send(
            {
                "jsonrpc": "2.0",
                "method": "textDocument/didChange",
                "params": {
                    "textDocument": {"uri": main.as_uri(), "version": 3},
                    "contentChanges": [{"text": completion_text}],
                },
            }
        )
        client.send(
            _request(
                6,
                "textDocument/completion",
                {
                    "textDocument": {"uri": main.as_uri()},
                    "position": {
                        "line": completion_line_number,
                        "character": len(completion_line.rstrip("\n")),
                    },
                },
            )
        )
        completion_items = client.response(6)["result"]["items"]
        alpha = next(
            item for item in completion_items if item["filterText"] == "\\alpha"
        )
        assert alpha["textEdit"]["newText"] == "α"
        assert alpha["textEdit"]["range"] == {
            "start": {"line": completion_line_number, "character": 11},
            "end": {"line": completion_line_number, "character": 15},
        }

        client.shutdown()
    finally:
        client.close()

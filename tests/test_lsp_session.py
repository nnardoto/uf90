from io import BytesIO
from pathlib import Path
import sys

import pytest

from uf90.lsp import JsonRpcProtocolError, read_message, run_proxy, write_message
from uf90.lsp_session import (
    FULL_DOCUMENT_SYNC,
    LspSession,
    file_uri_to_path,
    generated_uri,
)


def notification(method: str, params: dict) -> dict:
    return {"jsonrpc": "2.0", "method": method, "params": params}


def test_generated_uri_changes_only_f90u_suffix():
    assert generated_uri("file:///project/model.f90u") == "file:///project/model.f90"
    assert generated_uri("file:///project/MODEL.F90U") == "file:///project/MODEL.f90"
    assert generated_uri("file:///project/manual.f90") == "file:///project/manual.f90"
    assert generated_uri("untitled:model.f90u") == "untitled:model.f90"


def test_file_uri_is_decoded_exactly_once():
    assert file_uri_to_path("file:///tmp/a%2520b.f90u") == Path("/tmp/a%20b.f90u")
    assert file_uri_to_path("https://example.test/model.f90u") is None


def test_initialize_syncs_workspace_once_and_advertises_full_sync(tmp_path: Path):
    synced: list[Path] = []
    session = LspSession(sync=lambda root: synced.append(root) or 0)
    initialize = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "initialize",
        "params": {"rootUri": tmp_path.as_uri()},
    }

    assert session.client_to_server(initialize) is initialize
    session.client_to_server(initialize)
    assert synced == [tmp_path]

    response = {
        "jsonrpc": "2.0",
        "id": 4,
        "result": {"capabilities": {"textDocumentSync": 2}},
    }
    translated = session.server_to_client(response)
    assert translated["result"]["capabilities"]["textDocumentSync"] == {
        "openClose": True,
        "change": FULL_DOCUMENT_SYNC,
        "save": {"includeText": True},
    }
    assert translated["result"]["capabilities"]["completionProvider"] is None
    assert translated["result"]["capabilities"]["signatureHelpProvider"] is None
    assert translated["result"]["capabilities"]["renameProvider"] is False
    assert translated["result"]["capabilities"]["codeActionProvider"] is False
    assert response["result"]["capabilities"]["textDocumentSync"] == 2
    assert session.server_to_client(response) is response


def test_initialize_performs_real_project_sync_before_forwarding(tmp_path: Path):
    source = tmp_path / "model.f90u"
    source.write_text("real :: α\n", encoding="utf-8")
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"rootUri": tmp_path.as_uri()},
    }

    LspSession().client_to_server(initialize)

    assert source.with_suffix(".f90").read_text(encoding="utf-8") == "real :: uc_alpha\n"


def test_session_transforms_initialize_through_proxy(tmp_path: Path):
    source = tmp_path / "model.f90u"
    source.write_text("real :: α\n", encoding="utf-8")
    server = tmp_path / "initialize_server.py"
    server.write_text(
        """
import json
import sys

header = sys.stdin.buffer.readline()
length = int(header.decode().split(':', 1)[1])
assert sys.stdin.buffer.readline() == b'\\r\\n'
request = json.loads(sys.stdin.buffer.read(length))
response = {
    'jsonrpc': '2.0',
    'id': request['id'],
    'result': {'capabilities': {'textDocumentSync': 2}},
}
body = json.dumps(response, separators=(',', ':')).encode()
sys.stdout.buffer.write(f'Content-Length: {len(body)}\\r\\n\\r\\n'.encode() + body)
sys.stdout.buffer.flush()
""".lstrip(),
        encoding="utf-8",
    )
    request_stream = BytesIO()
    write_message(
        request_stream,
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "initialize",
            "params": {"rootUri": tmp_path.as_uri()},
        },
    )
    request_stream.seek(0)
    output = BytesIO()
    session = LspSession()

    assert run_proxy(
        [str(server)],
        stdin=request_stream,
        stdout=output,
        env={"UF90_FORTLS_PATH": sys.executable},
        client_transform=session.client_to_server,
        server_transform=session.server_to_client,
    ) == 0

    response = read_message(BytesIO(output.getvalue()))
    assert response is not None
    assert response["result"]["capabilities"]["textDocumentSync"]["change"] == 1
    assert source.with_suffix(".f90").exists()


def test_document_lifecycle_translates_in_memory_until_save(tmp_path: Path):
    source = tmp_path / "model.f90u"
    generated = tmp_path / "model.f90"
    source.write_text("real :: α\n", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    uri = source.as_uri()

    opened = session.client_to_server(
        notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": "FortranFreeForm",
                    "version": 1,
                    "text": "real :: α\n",
                }
            },
        )
    )
    assert opened["params"]["textDocument"]["uri"] == generated.as_uri()
    assert opened["params"]["textDocument"]["text"] == "real :: uc_alpha\n"
    assert not generated.exists()

    changed = session.client_to_server(
        notification(
            "textDocument/didChange",
            {
                "textDocument": {"uri": uri, "version": 2},
                "contentChanges": [{"text": "real :: β\n"}],
            },
        )
    )
    assert changed["params"]["textDocument"]["uri"] == generated.as_uri()
    assert changed["params"]["contentChanges"] == [{"text": "real :: uc_beta\n"}]
    assert not generated.exists()

    saved = session.client_to_server(
        notification("textDocument/didSave", {"textDocument": {"uri": uri}})
    )
    assert saved["params"]["textDocument"]["uri"] == generated.as_uri()
    assert generated.read_text(encoding="utf-8") == "real :: uc_beta\n"

    closed = session.client_to_server(
        notification("textDocument/didClose", {"textDocument": {"uri": uri}})
    )
    assert closed["params"]["textDocument"]["uri"] == generated.as_uri()
    with pytest.raises(JsonRpcProtocolError, match="before didOpen"):
        session.client_to_server(
            notification("textDocument/didSave", {"textDocument": {"uri": uri}})
        )


def test_did_save_prefers_included_full_text(tmp_path: Path):
    source = tmp_path / "included.f90u"
    session = LspSession(tmp_path, sync=lambda root: 0)
    uri = source.as_uri()
    session.client_to_server(
        notification(
            "textDocument/didOpen",
            {"textDocument": {"uri": uri, "version": 1, "text": "real :: α\n"}},
        )
    )

    saved = session.client_to_server(
        notification(
            "textDocument/didSave",
            {"textDocument": {"uri": uri}, "text": "real :: γ\n"},
        )
    )

    assert saved["params"]["text"] == "real :: uc_gamma\n"
    assert source.with_suffix(".f90").read_text(encoding="utf-8") == saved["params"]["text"]


def test_manual_f90_documents_pass_through_unchanged():
    session = LspSession(sync=lambda root: 0)
    message = notification(
        "textDocument/didOpen",
        {
            "textDocument": {
                "uri": "file:///project/manual.f90",
                "version": 1,
                "text": "real :: x\n",
            }
        },
    )

    assert session.client_to_server(message) is message


def test_incremental_changes_are_rejected(tmp_path: Path):
    uri = (tmp_path / "model.f90u").as_uri()
    session = LspSession(sync=lambda root: 0)
    session.client_to_server(
        notification(
            "textDocument/didOpen",
            {"textDocument": {"uri": uri, "version": 1, "text": "α\n"}},
        )
    )

    with pytest.raises(JsonRpcProtocolError, match="full-document"):
        session.client_to_server(
            notification(
                "textDocument/didChange",
                {
                    "textDocument": {"uri": uri, "version": 2},
                    "contentChanges": [
                        {
                            "range": {
                                "start": {"line": 0, "character": 0},
                                "end": {"line": 0, "character": 1},
                            },
                            "text": "β",
                        }
                    ],
                },
            )
        )

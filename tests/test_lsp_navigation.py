from pathlib import Path

import pytest

from uf90.lsp_session import LspSession


def request(request_id: int, method: str, params: dict) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params,
    }


def position(line: int, character: int) -> dict:
    return {"line": line, "character": character}


def range_(line: int, start: int, end: int) -> dict:
    return {"start": position(line, start), "end": position(line, end)}


def open_unicode(session: LspSession, source: Path, text: str) -> None:
    session.client_to_server(
        {
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": source.as_uri(),
                    "version": 1,
                    "text": text,
                }
            },
        }
    )


def test_hover_request_and_range_are_mapped_bidirectionally(tmp_path: Path):
    source = tmp_path / "model.f90u"
    source.write_text("real :: α\n", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    open_unicode(session, source, "real :: α\n")

    forwarded = session.client_to_server(
        request(
            10,
            "textDocument/hover",
            {
                "textDocument": {"uri": source.as_uri()},
                "position": position(0, 9),
            },
        )
    )
    assert forwarded["params"]["textDocument"]["uri"] == source.with_suffix(
        ".f90"
    ).as_uri()
    assert forwarded["params"]["position"] == position(0, 16)

    response = {
        "jsonrpc": "2.0",
        "id": 10,
        "result": {"contents": "real :: uc_alpha", "range": range_(0, 8, 16)},
    }
    translated = session.server_to_client(response)
    assert translated["result"]["range"] == range_(0, 8, 9)
    assert translated["result"]["contents"] == "real :: α"


def test_hover_translates_markup_and_marked_string_values(tmp_path: Path):
    source = tmp_path / "hover.f90u"
    source.write_text("real :: ω, E₀\n", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    open_unicode(session, source, "real :: ω, E₀\n")
    session.client_to_server(
        request(
            12,
            "textDocument/hover",
            {
                "textDocument": {"uri": source.as_uri()},
                "position": position(0, 8),
            },
        )
    )

    translated = session.server_to_client(
        {
            "jsonrpc": "2.0",
            "id": 12,
            "result": {
                "contents": [
                    {"language": "fortran", "value": "REAL :: uc_omega"},
                    {"kind": "markdown", "value": "Energy `E_0` and uc_omega"},
                    "uc_omega",
                ]
            },
        }
    )

    assert translated["result"]["contents"] == [
        {"language": "fortran", "value": "REAL :: ω"},
        {"kind": "markdown", "value": "Energy `E₀` and ω"},
        "ω",
    ]


def test_hover_restores_calculus_prefixed_identifiers(tmp_path: Path):
    source = tmp_path / "calculus.f90u"
    source.write_text("real :: ∂x, ∇φ\n", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    open_unicode(session, source, "real :: ∂x, ∇φ\n")
    session.client_to_server(
        request(
            14,
            "textDocument/hover",
            {
                "textDocument": {"uri": source.as_uri()},
                "position": position(0, 9),
            },
        )
    )

    translated = session.server_to_client(
        {
            "jsonrpc": "2.0",
            "id": 14,
            "result": {"contents": "real :: partial_x, nabla_phi"},
        }
    )

    assert translated["result"]["contents"] == "real :: ∂x, ∇φ"


def test_hover_keeps_ambiguous_generated_name_in_ascii(tmp_path: Path):
    source = tmp_path / "collision.f90u"
    source.write_text("real :: α, Α\n", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    open_unicode(session, source, "real :: α, Α\n")
    session.client_to_server(
        request(
            13,
            "textDocument/hover",
            {
                "textDocument": {"uri": source.as_uri()},
                "position": position(0, 8),
            },
        )
    )

    translated = session.server_to_client(
        {
            "jsonrpc": "2.0",
            "id": 13,
            "result": {"contents": "real :: uc_alpha"},
        }
    )

    assert translated["result"]["contents"] == "real :: uc_alpha"


@pytest.mark.parametrize(
    "method",
    [
        "textDocument/definition",
        "textDocument/declaration",
        "textDocument/typeDefinition",
        "textDocument/implementation",
        "textDocument/references",
    ],
)
def test_read_only_position_requests_use_generated_document(
    tmp_path: Path, method: str
):
    source = tmp_path / "requests.f90u"
    source.write_text("real :: α\n", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    open_unicode(session, source, "real :: α\n")
    params = {
        "textDocument": {"uri": source.as_uri()},
        "position": position(0, 9),
    }
    if method == "textDocument/references":
        params["context"] = {"includeDeclaration": True}

    forwarded = session.client_to_server(request(11, method, params))

    assert forwarded["params"]["textDocument"]["uri"] == source.with_suffix(
        ".f90"
    ).as_uri()
    assert forwarded["params"]["position"] == position(0, 16)
    assert session.server_to_client(
        {"jsonrpc": "2.0", "id": 11, "result": []}
    )["result"] == []


def test_negotiated_utf8_encoding_is_used_for_positions(tmp_path: Path):
    source = tmp_path / "utf8.f90u"
    source.write_text("😀α", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    session.client_to_server(
        request(1, "initialize", {"rootUri": tmp_path.as_uri()})
    )
    session.server_to_client(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "capabilities": {
                    "positionEncoding": "utf-8",
                    "textDocumentSync": 2,
                }
            },
        }
    )
    open_unicode(session, source, "😀α")

    forwarded = session.client_to_server(
        request(
            2,
            "textDocument/hover",
            {
                "textDocument": {"uri": source.as_uri()},
                "position": position(0, 6),
            },
        )
    )

    assert forwarded["params"]["position"] == position(0, 12)


def test_definition_maps_locations_and_location_links_across_files(tmp_path: Path):
    origin = tmp_path / "origin.f90u"
    target = tmp_path / "target.f90u"
    origin.write_text("real :: α\n", encoding="utf-8")
    target.write_text("real :: β\n", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    open_unicode(session, origin, "real :: α\n")
    session.client_to_server(
        request(
            20,
            "textDocument/definition",
            {
                "textDocument": {"uri": origin.as_uri()},
                "position": position(0, 8),
            },
        )
    )

    response = {
        "jsonrpc": "2.0",
        "id": 20,
        "result": [
            {"uri": target.with_suffix(".f90").as_uri(), "range": range_(0, 8, 15)},
            {
                "originSelectionRange": range_(0, 8, 16),
                "targetUri": target.with_suffix(".f90").as_uri(),
                "targetRange": range_(0, 8, 15),
                "targetSelectionRange": range_(0, 8, 15),
            },
            {"uri": "file:///external/manual.f90", "range": range_(2, 3, 7)},
        ],
    }
    translated = session.server_to_client(response)["result"]

    assert translated[0] == {"uri": target.as_uri(), "range": range_(0, 8, 9)}
    assert translated[1]["originSelectionRange"] == range_(0, 8, 9)
    assert translated[1]["targetUri"] == target.as_uri()
    assert translated[1]["targetRange"] == range_(0, 8, 9)
    assert translated[1]["targetSelectionRange"] == range_(0, 8, 9)
    assert translated[2] == response["result"][2]


def test_document_and_workspace_symbols_are_mapped(tmp_path: Path):
    source = tmp_path / "symbols.f90u"
    source.write_text("real :: α\n", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    open_unicode(session, source, "real :: α\n")
    session.client_to_server(
        request(
            30,
            "textDocument/documentSymbol",
            {"textDocument": {"uri": source.as_uri()}},
        )
    )

    document_symbols = session.server_to_client(
        {
            "jsonrpc": "2.0",
            "id": 30,
            "result": [
                {
                    "name": "uc_alpha",
                    "range": range_(0, 0, 16),
                    "selectionRange": range_(0, 8, 16),
                    "children": [
                        {
                            "name": "child",
                            "range": range_(0, 8, 16),
                            "selectionRange": range_(0, 8, 16),
                        }
                    ],
                }
            ],
        }
    )["result"]
    assert document_symbols[0]["range"] == range_(0, 0, 9)
    assert document_symbols[0]["selectionRange"] == range_(0, 8, 9)
    assert document_symbols[0]["children"][0]["range"] == range_(0, 8, 9)

    session.client_to_server(request(31, "workspace/symbol", {"query": "alpha"}))
    workspace_symbols = session.server_to_client(
        {
            "jsonrpc": "2.0",
            "id": 31,
            "result": [
                {
                    "name": "uc_alpha",
                    "kind": 13,
                    "location": {
                        "uri": source.with_suffix(".f90").as_uri(),
                        "range": range_(0, 8, 16),
                    },
                }
            ],
        }
    )["result"]
    assert workspace_symbols[0]["location"] == {
        "uri": source.as_uri(),
        "range": range_(0, 8, 9),
    }


def test_diagnostics_and_related_locations_are_mapped(tmp_path: Path):
    source = tmp_path / "diagnostic.f90u"
    related = tmp_path / "related.f90u"
    source.write_text("real :: α\n", encoding="utf-8")
    related.write_text("real :: β\n", encoding="utf-8")
    session = LspSession(tmp_path, sync=lambda root: 0)
    open_unicode(session, source, "real :: α\n")

    message = {
        "jsonrpc": "2.0",
        "method": "textDocument/publishDiagnostics",
        "params": {
            "uri": source.with_suffix(".f90").as_uri(),
            "diagnostics": [
                {
                    "range": range_(0, 8, 16),
                    "severity": 1,
                    "message": "unknown uc_alpha",
                    "relatedInformation": [
                        {
                            "location": {
                                "uri": related.with_suffix(".f90").as_uri(),
                                "range": range_(0, 8, 15),
                            },
                            "message": "declared here",
                        }
                    ],
                }
            ],
        },
    }
    translated = session.server_to_client(message)

    assert translated["params"]["uri"] == source.as_uri()
    diagnostic = translated["params"]["diagnostics"][0]
    assert diagnostic["range"] == range_(0, 8, 9)
    assert diagnostic["message"] == "unknown uc_alpha"
    assert diagnostic["relatedInformation"][0]["location"] == {
        "uri": related.as_uri(),
        "range": range_(0, 8, 9),
    }


def test_manual_fortran_hover_and_locations_remain_unchanged():
    session = LspSession(sync=lambda root: 0)
    hover = request(
        40,
        "textDocument/hover",
        {
            "textDocument": {"uri": "file:///external/manual.f90"},
            "position": position(3, 4),
        },
    )
    assert session.client_to_server(hover) is hover
    response = {
        "jsonrpc": "2.0",
        "id": 40,
        "result": {"contents": "x", "range": range_(3, 2, 5)},
    }
    assert session.server_to_client(response) == response


def test_unopened_pair_preserves_exact_source_extension_case(tmp_path: Path):
    source = tmp_path / "MODEL.F90U"
    source.write_text("real :: α\n", encoding="utf-8")
    generated = tmp_path / "MODEL.f90"
    session = LspSession(tmp_path, sync=lambda root: 0)
    session.client_to_server(request(50, "workspace/symbol", {"query": "alpha"}))

    translated = session.server_to_client(
        {
            "jsonrpc": "2.0",
            "id": 50,
            "result": [
                {
                    "name": "uc_alpha",
                    "kind": 13,
                    "location": {
                        "uri": generated.as_uri(),
                        "range": range_(0, 8, 16),
                    },
                }
            ],
        }
    )

    assert translated["result"][0]["location"] == {
        "uri": source.as_uri(),
        "range": range_(0, 8, 9),
    }

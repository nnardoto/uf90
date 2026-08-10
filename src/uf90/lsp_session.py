from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from urllib.request import url2pathname

from .lsp import JsonRpcProtocolError
from .sync import sync_project
from .translator import TranslationResult, translate_with_map


FULL_DOCUMENT_SYNC = 1


def generated_uri(source_uri: str) -> str:
    """Return the adjacent generated URI for a .f90u source URI."""

    parsed = urlsplit(source_uri)
    if not parsed.path.lower().endswith(".f90u"):
        return source_uri
    generated_path = f"{parsed.path[:-5]}.f90"
    return urlunsplit(
        (parsed.scheme, parsed.netloc, generated_path, parsed.query, parsed.fragment)
    )


def file_uri_to_path(uri: str) -> Path | None:
    parsed = urlsplit(uri)
    if parsed.scheme.lower() != "file" or parsed.netloc not in {"", "localhost"}:
        return None
    return Path(url2pathname(parsed.path))


@dataclass
class OpenDocument:
    source_uri: str
    generated_uri: str
    version: int | None
    source_text: str
    translation: TranslationResult


class LspSession:
    """Stateful, method-specific translation for one LSP connection."""

    def __init__(
        self,
        root: Path | None = None,
        sync: Callable[[Path], int] = sync_project,
    ) -> None:
        self.root = Path.cwd() if root is None else Path(root)
        self._sync = sync
        self._synced = False
        self._initialize_id: str | int | None = None
        self._initialize_pending = False
        self._documents: dict[str, OpenDocument] = {}

    def client_to_server(self, message: dict[str, Any]) -> Mapping[str, Any]:
        method = message.get("method")
        if method == "initialize":
            return self._initialize(message)
        if method == "textDocument/didOpen":
            return self._did_open(message)
        if method == "textDocument/didChange":
            return self._did_change(message)
        if method == "textDocument/didSave":
            return self._did_save(message)
        if method == "textDocument/didClose":
            return self._did_close(message)
        return message

    def server_to_client(self, message: dict[str, Any]) -> Mapping[str, Any]:
        if not self._initialize_pending or message.get("id") != self._initialize_id:
            return message
        self._initialize_pending = False
        if "result" not in message:
            return message
        result = message.get("result")
        if not isinstance(result, dict):
            return message
        capabilities = result.get("capabilities")
        if not isinstance(capabilities, dict):
            return message

        translated = deepcopy(message)
        translated_capabilities = translated["result"]["capabilities"]
        translated_capabilities["textDocumentSync"] = {
            "openClose": True,
            "change": FULL_DOCUMENT_SYNC,
            "save": {"includeText": True},
        }
        return translated

    def _initialize(self, message: dict[str, Any]) -> Mapping[str, Any]:
        self._initialize_id = message.get("id")
        self._initialize_pending = True
        if not self._synced:
            self.root = self._workspace_root(message) or self.root
            self._sync(self.root)
            self._synced = True
        return message

    def _workspace_root(self, message: dict[str, Any]) -> Path | None:
        params = message.get("params")
        if not isinstance(params, dict):
            return None

        root_uri = params.get("rootUri")
        if isinstance(root_uri, str):
            path = file_uri_to_path(root_uri)
            if path is not None:
                return path

        root_path = params.get("rootPath")
        if isinstance(root_path, str):
            return Path(root_path)

        folders = params.get("workspaceFolders")
        if isinstance(folders, list) and folders:
            first = folders[0]
            if isinstance(first, dict) and isinstance(first.get("uri"), str):
                return file_uri_to_path(first["uri"])
        return None

    def _did_open(self, message: dict[str, Any]) -> Mapping[str, Any]:
        params = self._params(message)
        text_document = self._text_document(params)
        uri = self._string_field(text_document, "uri")
        if generated_uri(uri) == uri:
            return message
        text = self._string_field(text_document, "text")
        version = text_document.get("version")
        if version is not None and not isinstance(version, int):
            raise JsonRpcProtocolError("didOpen version must be an integer or null")

        translation = translate_with_map(text)
        document = OpenDocument(
            source_uri=uri,
            generated_uri=generated_uri(uri),
            version=version,
            source_text=text,
            translation=translation,
        )
        self._documents[uri] = document

        translated = deepcopy(message)
        target = translated["params"]["textDocument"]
        target["uri"] = document.generated_uri
        target["text"] = translation.text
        return translated

    def _did_change(self, message: dict[str, Any]) -> Mapping[str, Any]:
        params = self._params(message)
        text_document = self._text_document(params)
        uri = self._string_field(text_document, "uri")
        if generated_uri(uri) == uri:
            return message
        document = self._open_document(uri, "didChange")

        changes = params.get("contentChanges")
        if not isinstance(changes, list) or not changes:
            raise JsonRpcProtocolError("didChange requires contentChanges")
        for change in changes:
            if not isinstance(change, dict) or not isinstance(change.get("text"), str):
                raise JsonRpcProtocolError("didChange contains an invalid content change")
            if "range" in change:
                raise JsonRpcProtocolError(
                    "uf90-ls requires full-document didChange notifications"
                )

        source_text = changes[-1]["text"]
        translation = translate_with_map(source_text)
        version = text_document.get("version")
        if version is not None and not isinstance(version, int):
            raise JsonRpcProtocolError("didChange version must be an integer or null")
        document.source_text = source_text
        document.translation = translation
        document.version = version

        translated = deepcopy(message)
        translated["params"]["textDocument"]["uri"] = document.generated_uri
        translated["params"]["contentChanges"] = [{"text": translation.text}]
        return translated

    def _did_save(self, message: dict[str, Any]) -> Mapping[str, Any]:
        params = self._params(message)
        text_document = self._text_document(params)
        uri = self._string_field(text_document, "uri")
        if generated_uri(uri) == uri:
            return message
        document = self._open_document(uri, "didSave")

        saved_text = params.get("text")
        if saved_text is not None:
            if not isinstance(saved_text, str):
                raise JsonRpcProtocolError("didSave text must be a string or null")
            document.source_text = saved_text
            document.translation = translate_with_map(saved_text)

        generated_path = file_uri_to_path(document.generated_uri)
        if generated_path is not None:
            generated_path.write_text(document.translation.text, encoding="utf-8")

        translated = deepcopy(message)
        translated["params"]["textDocument"]["uri"] = document.generated_uri
        if saved_text is not None:
            translated["params"]["text"] = document.translation.text
        return translated

    def _did_close(self, message: dict[str, Any]) -> Mapping[str, Any]:
        params = self._params(message)
        text_document = self._text_document(params)
        uri = self._string_field(text_document, "uri")
        if generated_uri(uri) == uri:
            return message
        document = self._open_document(uri, "didClose")

        translated = deepcopy(message)
        translated["params"]["textDocument"]["uri"] = document.generated_uri
        del self._documents[uri]
        return translated

    @staticmethod
    def _params(message: dict[str, Any]) -> dict[str, Any]:
        params = message.get("params")
        if not isinstance(params, dict):
            raise JsonRpcProtocolError("LSP notification params must be an object")
        return params

    @staticmethod
    def _text_document(params: dict[str, Any]) -> dict[str, Any]:
        text_document = params.get("textDocument")
        if not isinstance(text_document, dict):
            raise JsonRpcProtocolError("params.textDocument must be an object")
        return text_document

    @staticmethod
    def _string_field(container: dict[str, Any], name: str) -> str:
        value = container.get(name)
        if not isinstance(value, str):
            raise JsonRpcProtocolError(f"{name} must be a string")
        return value

    def _open_document(self, uri: str, method: str) -> OpenDocument:
        try:
            return self._documents[uri]
        except KeyError as exc:
            raise JsonRpcProtocolError(
                f"{method} received before didOpen for {uri}"
            ) from exc

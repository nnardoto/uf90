from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from urllib.request import url2pathname

from .lsp import JsonRpcProtocolError
from .sync import sync_project
from .translator import TranslationResult, translate_with_map


FULL_DOCUMENT_SYNC = 1

POSITION_REQUESTS = {
    "textDocument/hover",
    "textDocument/definition",
    "textDocument/declaration",
    "textDocument/typeDefinition",
    "textDocument/implementation",
    "textDocument/references",
}

LOCATION_RESULTS = {
    "textDocument/definition",
    "textDocument/declaration",
    "textDocument/typeDefinition",
    "textDocument/implementation",
    "textDocument/references",
}

ASCII_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


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


@dataclass(frozen=True)
class PendingRequest:
    method: str
    source_uri: str | None


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
        self._generated_sources: dict[str, str] = {}
        self._pending_requests: dict[str | int, PendingRequest] = {}
        self.position_encoding = "utf-16"

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
        if method in POSITION_REQUESTS:
            return self._position_request(message, method)
        if method == "textDocument/documentSymbol":
            return self._document_request(message, method)
        if method == "workspace/symbol":
            self._remember_request(message, PendingRequest(method, None))
            return message
        return message

    def server_to_client(self, message: dict[str, Any]) -> Mapping[str, Any]:
        if self._initialize_pending and message.get("id") == self._initialize_id:
            return self._initialize_response(message)
        if message.get("method") == "textDocument/publishDiagnostics":
            return self._publish_diagnostics(message)

        request_id = message.get("id")
        if "method" not in message and request_id in self._pending_requests:
            context = self._pending_requests.pop(request_id)
            return self._request_response(message, context)
        return message

    def _initialize_response(self, message: dict[str, Any]) -> Mapping[str, Any]:
        self._initialize_pending = False
        if "result" not in message:
            return message
        result = message.get("result")
        if not isinstance(result, dict):
            return message
        capabilities = result.get("capabilities")
        if not isinstance(capabilities, dict):
            return message

        position_encoding = capabilities.get("positionEncoding")
        if isinstance(position_encoding, str) and position_encoding.lower() in {
            "utf-8",
            "utf-16",
            "utf-32",
        }:
            self.position_encoding = position_encoding.lower()

        translated = deepcopy(message)
        translated_capabilities = translated["result"]["capabilities"]
        translated_capabilities["textDocumentSync"] = {
            "openClose": True,
            "change": FULL_DOCUMENT_SYNC,
            "save": {"includeText": True},
        }
        # These methods can return edits or generated ASCII names. Keep them
        # disabled until their results have dedicated, lossless translators.
        translated_capabilities["completionProvider"] = None
        translated_capabilities["signatureHelpProvider"] = None
        translated_capabilities["renameProvider"] = False
        translated_capabilities["codeActionProvider"] = False
        translated_capabilities["documentFormattingProvider"] = False
        translated_capabilities["documentRangeFormattingProvider"] = False
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
        self._generated_sources[document.generated_uri] = uri

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

    def _position_request(
        self, message: dict[str, Any], method: str
    ) -> Mapping[str, Any]:
        params = self._params(message)
        text_document = self._text_document(params)
        uri = self._string_field(text_document, "uri")
        self._remember_request(message, PendingRequest(method, uri))
        if generated_uri(uri) == uri:
            return message

        translated = deepcopy(message)
        translated["params"]["textDocument"]["uri"] = generated_uri(uri)
        translated["params"]["position"] = self._map_position(
            params.get("position"), uri, to_generated=True
        )
        return translated

    def _document_request(
        self, message: dict[str, Any], method: str
    ) -> Mapping[str, Any]:
        params = self._params(message)
        text_document = self._text_document(params)
        uri = self._string_field(text_document, "uri")
        self._remember_request(message, PendingRequest(method, uri))
        if generated_uri(uri) == uri:
            return message

        translated = deepcopy(message)
        translated["params"]["textDocument"]["uri"] = generated_uri(uri)
        return translated

    def _request_response(
        self, message: dict[str, Any], context: PendingRequest
    ) -> Mapping[str, Any]:
        if "result" not in message or message.get("result") is None:
            return message

        translated = deepcopy(message)
        result = translated.get("result")
        if context.method == "textDocument/hover":
            if isinstance(result, dict) and "contents" in result:
                result["contents"] = self._map_hover_contents(result["contents"])
            if (
                isinstance(result, dict)
                and "range" in result
                and context.source_uri
                and generated_uri(context.source_uri) != context.source_uri
            ):
                result["range"] = self._map_range(
                    result["range"], context.source_uri, to_generated=False
                )
        elif context.method in LOCATION_RESULTS:
            translated["result"] = self._map_location_result(
                result, context.source_uri
            )
        elif context.method in {"textDocument/documentSymbol", "workspace/symbol"}:
            translated["result"] = self._map_symbol_result(result, context.source_uri)
        return translated

    def _map_hover_contents(self, contents: Any) -> Any:
        symbols = self._presentation_symbols()

        def replace_identifiers(text: str) -> str:
            return ASCII_IDENTIFIER.sub(
                lambda match: symbols.get(match.group(0).casefold(), match.group(0)),
                text,
            )

        if isinstance(contents, str):
            return replace_identifiers(contents)
        if isinstance(contents, list):
            return [self._map_hover_value(item, replace_identifiers) for item in contents]
        return self._map_hover_value(contents, replace_identifiers)

    @staticmethod
    def _map_hover_value(
        value: Any, replace_identifiers: Callable[[str], str]
    ) -> Any:
        if isinstance(value, str):
            return replace_identifiers(value)
        if not isinstance(value, dict) or not isinstance(value.get("value"), str):
            return value
        translated = deepcopy(value)
        translated["value"] = replace_identifiers(translated["value"])
        return translated

    def _presentation_symbols(self) -> dict[str, str]:
        candidates: dict[str, set[str]] = {}
        open_paths: set[Path] = set()

        for document in self._documents.values():
            self._collect_symbols(document.translation, candidates)
            path = file_uri_to_path(document.source_uri)
            if path is not None:
                open_paths.add(path)

        if self.root.is_dir():
            for path in self.root.rglob("*"):
                if (
                    not path.is_file()
                    or path.suffix.lower() != ".f90u"
                    or path in open_paths
                ):
                    continue
                try:
                    translation = translate_with_map(path.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, ValueError):
                    continue
                self._collect_symbols(translation, candidates)

        return {
            generated: next(iter(sources))
            for generated, sources in candidates.items()
            if len(sources) == 1
        }

    @staticmethod
    def _collect_symbols(
        translation: TranslationResult, candidates: dict[str, set[str]]
    ) -> None:
        for line in translation.source_map.lines:
            for match in ASCII_IDENTIFIER.finditer(line.generated_text):
                source_start = line.generated_to_source[match.start()]
                source_end = line.generated_to_source[match.end()]
                source_name = line.source_text[source_start:source_end]
                generated_name = match.group(0)
                if source_name and source_name != generated_name:
                    candidates.setdefault(generated_name.casefold(), set()).add(
                        source_name
                    )

    def _publish_diagnostics(self, message: dict[str, Any]) -> Mapping[str, Any]:
        params = self._params(message)
        generated_document_uri = self._string_field(params, "uri")
        source_document_uri = self._source_uri(generated_document_uri)
        diagnostics = params.get("diagnostics")
        if not isinstance(diagnostics, list):
            raise JsonRpcProtocolError("publishDiagnostics requires diagnostics")

        translated = deepcopy(message)
        target_params = translated["params"]
        target_params["uri"] = source_document_uri
        for diagnostic in target_params["diagnostics"]:
            if not isinstance(diagnostic, dict):
                raise JsonRpcProtocolError("diagnostic must be an object")
            if source_document_uri != generated_document_uri:
                diagnostic["range"] = self._map_range(
                    diagnostic.get("range"), source_document_uri, to_generated=False
                )
            related = diagnostic.get("relatedInformation")
            if isinstance(related, list):
                for information in related:
                    if isinstance(information, dict) and isinstance(
                        information.get("location"), dict
                    ):
                        information["location"] = self._map_location(
                            information["location"]
                        )
        return translated

    def _map_location_result(
        self, result: Any, origin_uri: str | None
    ) -> Any:
        if isinstance(result, list):
            return [self._map_location_result(item, origin_uri) for item in result]
        if not isinstance(result, dict):
            return result
        if "targetUri" in result:
            return self._map_location_link(result, origin_uri)
        if "uri" in result:
            return self._map_location(result)
        return result

    def _map_location(self, location: dict[str, Any]) -> dict[str, Any]:
        generated_document_uri = self._string_field(location, "uri")
        source_document_uri = self._source_uri(generated_document_uri)
        translated = deepcopy(location)
        translated["uri"] = source_document_uri
        if "range" in translated and source_document_uri != generated_document_uri:
            translated["range"] = self._map_range(
                translated["range"], source_document_uri, to_generated=False
            )
        return translated

    def _map_location_link(
        self, link: dict[str, Any], origin_uri: str | None
    ) -> dict[str, Any]:
        generated_target_uri = self._string_field(link, "targetUri")
        source_target_uri = self._source_uri(generated_target_uri)
        translated = deepcopy(link)
        translated["targetUri"] = source_target_uri
        if source_target_uri != generated_target_uri:
            for field in ("targetRange", "targetSelectionRange"):
                if field in translated:
                    translated[field] = self._map_range(
                        translated[field], source_target_uri, to_generated=False
                    )
        if (
            origin_uri
            and generated_uri(origin_uri) != origin_uri
            and "originSelectionRange" in translated
        ):
            translated["originSelectionRange"] = self._map_range(
                translated["originSelectionRange"], origin_uri, to_generated=False
            )
        return translated

    def _map_symbol_result(self, result: Any, document_uri: str | None) -> Any:
        if isinstance(result, list):
            return [self._map_symbol_result(item, document_uri) for item in result]
        if not isinstance(result, dict):
            return result

        translated = deepcopy(result)
        location = translated.get("location")
        if isinstance(location, dict):
            translated["location"] = self._map_location(location)
        elif document_uri and generated_uri(document_uri) != document_uri:
            for field in ("range", "selectionRange"):
                if field in translated:
                    translated[field] = self._map_range(
                        translated[field], document_uri, to_generated=False
                    )
        children = translated.get("children")
        if isinstance(children, list):
            translated["children"] = [
                self._map_symbol_result(child, document_uri) for child in children
            ]
        return translated

    def _map_position(
        self, position: Any, source_document_uri: str, *, to_generated: bool
    ) -> dict[str, int]:
        if not isinstance(position, dict):
            raise JsonRpcProtocolError("position must be an object")
        line = position.get("line")
        character = position.get("character")
        if (
            not isinstance(line, int)
            or isinstance(line, bool)
            or line < 0
            or not isinstance(character, int)
            or isinstance(character, bool)
            or character < 0
        ):
            raise JsonRpcProtocolError(
                "position line and character must be non-negative integers"
            )

        source_map = self._translation(source_document_uri).source_map
        try:
            mapped_line, mapped_character = (
                source_map.to_generated(line, character, self.position_encoding)
                if to_generated
                else source_map.to_source(line, character, self.position_encoding)
            )
        except ValueError as exc:
            raise JsonRpcProtocolError(f"cannot map LSP position: {exc}") from exc
        return {"line": mapped_line, "character": mapped_character}

    def _map_range(
        self, range_value: Any, source_document_uri: str, *, to_generated: bool
    ) -> dict[str, dict[str, int]]:
        if not isinstance(range_value, dict):
            raise JsonRpcProtocolError("range must be an object")
        return {
            "start": self._map_position(
                range_value.get("start"), source_document_uri, to_generated=to_generated
            ),
            "end": self._map_position(
                range_value.get("end"), source_document_uri, to_generated=to_generated
            ),
        }

    def _translation(self, source_document_uri: str) -> TranslationResult:
        document = self._documents.get(source_document_uri)
        if document is not None:
            return document.translation
        source_path = file_uri_to_path(source_document_uri)
        if source_path is None or not source_path.is_file():
            raise JsonRpcProtocolError(
                f"Unicode source is unavailable for position mapping: {source_document_uri}"
            )
        return translate_with_map(source_path.read_text(encoding="utf-8"))

    def _source_uri(self, generated_document_uri: str) -> str:
        known_source = self._generated_sources.get(generated_document_uri)
        if known_source is not None:
            return known_source

        parsed = urlsplit(generated_document_uri)
        if not parsed.path.lower().endswith(".f90"):
            return generated_document_uri
        candidate_uri = urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                f"{parsed.path[:-4]}.f90u",
                parsed.query,
                parsed.fragment,
            )
        )
        generated_path = file_uri_to_path(generated_document_uri)
        if generated_path is not None and generated_path.parent.is_dir():
            for sibling in generated_path.parent.iterdir():
                if (
                    sibling.is_file()
                    and sibling.stem == generated_path.stem
                    and sibling.suffix.lower() == ".f90u"
                ):
                    exact_uri = sibling.as_uri()
                    self._generated_sources[generated_document_uri] = exact_uri
                    return exact_uri
        candidate_path = file_uri_to_path(candidate_uri)
        if candidate_path is not None and candidate_path.is_file():
            self._generated_sources[generated_document_uri] = candidate_uri
            return candidate_uri
        return generated_document_uri

    def _remember_request(
        self, message: dict[str, Any], context: PendingRequest
    ) -> None:
        request_id = message.get("id")
        if not isinstance(request_id, (str, int)) or isinstance(request_id, bool):
            raise JsonRpcProtocolError("LSP request id must be a string or integer")
        self._pending_requests[request_id] = context

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

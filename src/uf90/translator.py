from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import re

from .mapping import GREEK, SUBS, SUPS, is_fortran_ident_char, reserved_ascii_names


@dataclass(frozen=True)
class TranslateOptions:
    preserve_comments: bool = True
    uc_prefix: str = "uc_"


@dataclass(frozen=True)
class LineSourceMap:
    """Bidirectional character-boundary map for one physical source line."""

    source_text: str
    generated_text: str
    source_to_generated: tuple[int, ...]
    generated_to_source: tuple[int, ...]


@dataclass(frozen=True)
class SourceMap:
    """Map LSP positions between Unicode source and generated Fortran."""

    lines: tuple[LineSourceMap, ...]

    def to_generated(
        self, line: int, character: int, encoding: str = "utf-16"
    ) -> tuple[int, int]:
        line_map = self._line(line)
        source_index = _lsp_units_to_index(line_map.source_text, character, encoding)
        generated_index = line_map.source_to_generated[source_index]
        return line, _index_to_lsp_units(
            line_map.generated_text, generated_index, encoding
        )

    def to_source(
        self, line: int, character: int, encoding: str = "utf-16"
    ) -> tuple[int, int]:
        line_map = self._line(line)
        generated_index = _lsp_units_to_index(
            line_map.generated_text, character, encoding
        )
        source_index = line_map.generated_to_source[generated_index]
        return line, _index_to_lsp_units(line_map.source_text, source_index, encoding)

    def _line(self, line: int) -> LineSourceMap:
        if line < 0 or line >= len(self.lines):
            raise ValueError(f"line outside source map: {line}")
        return self.lines[line]


@dataclass(frozen=True)
class TranslationResult:
    text: str
    source_map: SourceMap


def _encoding_width(ch: str, encoding: str) -> int:
    normalized = encoding.lower().replace("_", "-")
    if normalized == "utf-8":
        return len(ch.encode("utf-8"))
    if normalized == "utf-16":
        return len(ch.encode("utf-16-le")) // 2
    if normalized in {"utf-32", "codepoint", "codepoints"}:
        return 1
    raise ValueError(f"unsupported position encoding: {encoding}")


def _lsp_units_to_index(text: str, character: int, encoding: str) -> int:
    """Convert an LSP character offset to a Python string boundary.

    Offsets beyond the line are clamped as required by the LSP. An offset in
    the middle of a multi-unit character uses that character's left boundary.
    """

    if character <= 0:
        return 0
    units = 0
    for index, ch in enumerate(text):
        next_units = units + _encoding_width(ch, encoding)
        if character < next_units:
            return index
        if character == next_units:
            return index + 1
        units = next_units
    return len(text)


def _index_to_lsp_units(text: str, index: int, encoding: str) -> int:
    return sum(_encoding_width(ch, encoding) for ch in text[:index])


class _MappedLineBuilder:
    def __init__(self) -> None:
        self.parts: list[str] = []
        self.source_length = 0
        self.generated_length = 0
        self.source_to_generated = [0]
        self.generated_to_source = [0]

    def emit(self, source: str, generated: str) -> None:
        source_start = self.source_length
        generated_start = self.generated_length
        self.parts.append(generated)

        if source == generated:
            for offset in range(1, len(source) + 1):
                self.source_to_generated.append(generated_start + offset)
                self.generated_to_source.append(source_start + offset)
        else:
            # A replacement is atomic. Boundaries inside an expanded spelling
            # map to the beginning of the Unicode fragment; its final boundary
            # maps to the fragment's final boundary.
            for _ in source[:-1]:
                self.source_to_generated.append(generated_start)
            self.source_to_generated.append(generated_start + len(generated))
            for _ in generated[:-1]:
                self.generated_to_source.append(source_start)
            self.generated_to_source.append(source_start + len(source))

        self.source_length += len(source)
        self.generated_length += len(generated)

    @property
    def text(self) -> str:
        return "".join(self.parts)


# Token ASCII simples de identificador Fortran. Ele é usado apenas para a
# validação dos nomes que pertencem ao namespace reservado do uf90.
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _is_ident_start(ch: str) -> bool:
    return (ch.isascii() and (ch.isalpha() or ch == "_")) or ch in GREEK


def _is_ident_char(ch: str) -> bool:
    return (
        (ch.isascii() and (ch.isalnum() or ch == "_"))
        or ch in GREEK
        or ch in SUBS
        or ch in SUPS
    )


def _translate_identifier_pieces(
    s: str, opt: TranslateOptions
) -> list[tuple[str, str]]:
    pieces: list[tuple[str, str]] = []
    generated = ""
    i = 0
    while i < len(s):
        ch = s[i]

        if ch in GREEK:
            name = GREEK[ch]
            # se não estamos "dentro" de um identificador, prefixa com uc_
            if generated and is_fortran_ident_char(generated[-1:]):
                replacement = name
            else:
                replacement = opt.uc_prefix + name.lower()
            pieces.append((ch, replacement))
            generated += replacement
            i += 1
            continue

        if ch in SUBS:
            first = True
            while i < len(s) and s[i] in SUBS:
                replacement = ("_" if first else "") + SUBS[s[i]]
                pieces.append((s[i], replacement))
                generated += replacement
                first = False
                i += 1
            continue

        if ch in SUPS:
            first = True
            while i < len(s) and s[i] in SUPS:
                replacement = ("_p" if first else "") + SUPS[s[i]]
                pieces.append((s[i], replacement))
                generated += replacement
                first = False
                i += 1
            continue

        pieces.append((ch, ch))
        generated += ch
        i += 1

    return pieces


def _translate_identifier_fragment(s: str, opt: TranslateOptions) -> str:
    return "".join(generated for _, generated in _translate_identifier_pieces(s, opt))


def _validate_ascii_identifier(token: str, bad: set[str]) -> None:
    if _IDENT.fullmatch(token) and token.lower() in bad:
        raise ValueError(
            f"Identificador ASCII reservado encontrado no fonte unicode: '{token}'. "
            "Use o símbolo Unicode correspondente ou renomeie o identificador."
        )


def _translate_line(
    line: str,
    opt: TranslateOptions,
    bad: set[str],
    quote: str | None,
) -> tuple[str, str | None, tuple[int, ...], tuple[int, ...]]:
    """Translate identifiers while leaving character literals untouched.

    ``quote`` carries a continued Fortran character literal from the previous
    physical line. Comments are recognized only outside character literals, so
    an exclamation mark inside a string does not truncate the source line.
    """

    out = _MappedLineBuilder()
    i = 0

    while i < len(line):
        ch = line[i]

        if quote is not None:
            out.emit(ch, ch)
            if ch == quote:
                # Fortran escapes a quote by doubling it.
                if i + 1 < len(line) and line[i + 1] == quote:
                    out.emit(line[i + 1], line[i + 1])
                    i += 2
                    continue
                quote = None
            i += 1
            continue

        if ch in ("'", '"'):
            quote = ch
            out.emit(ch, ch)
            i += 1
            continue

        if ch == "!":
            if opt.preserve_comments:
                out.emit(line[i:], line[i:])
            else:
                fragment = line[i:]
                for source, generated in _translate_identifier_pieces(fragment, opt):
                    out.emit(source, generated)
            break

        if _is_ident_start(ch):
            end = i + 1
            while end < len(line) and _is_ident_char(line[end]):
                end += 1
            token = line[i:end]
            _validate_ascii_identifier(token, bad)
            for source, generated in _translate_identifier_pieces(token, opt):
                out.emit(source, generated)
            i = end
            continue

        out.emit(ch, ch)
        i += 1

    # A valid continued character literal ends the physical line with '&'. If
    # it does not, reset the state so a malformed line cannot hide the rest of
    # the file from translation and validation.
    if quote is not None and not line.rstrip("\r\n").rstrip().endswith("&"):
        quote = None

    return (
        out.text,
        quote,
        tuple(out.source_to_generated),
        tuple(out.generated_to_source),
    )


def translate_text(text: str, opt: TranslateOptions = TranslateOptions()) -> str:
    return translate_with_map(text, opt).text


def _line_ending_length(line: str) -> int:
    if line.endswith("\r\n"):
        return 2
    if line.endswith(("\n", "\r")):
        return 1
    return 0


def translate_with_map(
    text: str, opt: TranslateOptions = TranslateOptions()
) -> TranslationResult:
    lines = text.splitlines(keepends=True)
    out_lines: list[str] = []
    line_maps: list[LineSourceMap] = []

    # Checa apenas tokens (evita falso positivo por substring)
    bad = {x.lower() for x in reserved_ascii_names()}

    quote: str | None = None
    for line in lines:
        translated, quote, source_to_generated, generated_to_source = _translate_line(
            line, opt, bad, quote
        )
        out_lines.append(translated)

        source_ending = _line_ending_length(line)
        generated_ending = _line_ending_length(translated)
        source_content_length = len(line) - source_ending
        generated_content_length = len(translated) - generated_ending
        line_maps.append(
            LineSourceMap(
                source_text=line[:source_content_length],
                generated_text=translated[:generated_content_length],
                source_to_generated=source_to_generated[: source_content_length + 1],
                generated_to_source=generated_to_source[: generated_content_length + 1],
            )
        )

    # LSP positions can address the empty logical line after a final newline.
    if not lines or _line_ending_length(lines[-1]):
        line_maps.append(LineSourceMap("", "", (0,), (0,)))

    return TranslationResult("".join(out_lines), SourceMap(tuple(line_maps)))


def translate_file(src: Path, dst: Path | None = None, opt: TranslateOptions = TranslateOptions()) -> Path:
    src = Path(src)
    if dst is None:
        dst = src.with_suffix(".f90") if src.suffix.lower() == ".f90u" else src.with_suffix(src.suffix + ".f90")

    text = src.read_text(encoding="utf-8")
    out = translate_text(text, opt)

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    return dst


def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

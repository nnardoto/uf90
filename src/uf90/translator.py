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


def _translate_identifier_fragment(s: str, opt: TranslateOptions) -> str:
    out: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]

        if ch in GREEK:
            name = GREEK[ch]
            # se não estamos "dentro" de um identificador, prefixa com uc_
            if out and is_fortran_ident_char(out[-1][-1:]):
                out.append(name)
            else:
                out.append(opt.uc_prefix + name.lower())
            i += 1
            continue

        if ch in SUBS:
            digits = []
            while i < len(s) and s[i] in SUBS:
                digits.append(SUBS[s[i]])
                i += 1
            out.append("_" + "".join(digits))
            continue

        if ch in SUPS:
            digits = []
            while i < len(s) and s[i] in SUPS:
                digits.append(SUPS[s[i]])
                i += 1
            out.append("_p" + "".join(digits))
            continue

        out.append(ch)
        i += 1

    return "".join(out)


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
) -> tuple[str, str | None]:
    """Translate identifiers while leaving character literals untouched.

    ``quote`` carries a continued Fortran character literal from the previous
    physical line. Comments are recognized only outside character literals, so
    an exclamation mark inside a string does not truncate the source line.
    """

    out: list[str] = []
    i = 0

    while i < len(line):
        ch = line[i]

        if quote is not None:
            out.append(ch)
            if ch == quote:
                # Fortran escapes a quote by doubling it.
                if i + 1 < len(line) and line[i + 1] == quote:
                    out.append(line[i + 1])
                    i += 2
                    continue
                quote = None
            i += 1
            continue

        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            i += 1
            continue

        if ch == "!":
            if opt.preserve_comments:
                out.append(line[i:])
            else:
                out.append(_translate_identifier_fragment(line[i:], opt))
            break

        if _is_ident_start(ch):
            end = i + 1
            while end < len(line) and _is_ident_char(line[end]):
                end += 1
            token = line[i:end]
            _validate_ascii_identifier(token, bad)
            out.append(_translate_identifier_fragment(token, opt))
            i = end
            continue

        out.append(ch)
        i += 1

    # A valid continued character literal ends the physical line with '&'. If
    # it does not, reset the state so a malformed line cannot hide the rest of
    # the file from translation and validation.
    if quote is not None and not line.rstrip("\r\n").rstrip().endswith("&"):
        quote = None

    return "".join(out), quote


def translate_text(text: str, opt: TranslateOptions = TranslateOptions()) -> str:
    lines = text.splitlines(keepends=True)
    out_lines: list[str] = []

    # Checa apenas tokens (evita falso positivo por substring)
    bad = {x.lower() for x in reserved_ascii_names()}

    quote: str | None = None
    for line in lines:
        translated, quote = _translate_line(line, opt, bad, quote)
        out_lines.append(translated)

    return "".join(out_lines)


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

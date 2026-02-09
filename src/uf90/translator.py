from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib

from .mapping import GREEK, SUBS, SUPS, is_fortran_ident_char, reserved_ascii_names


@dataclass(frozen=True)
class TranslateOptions:
    preserve_comments: bool = True
    uc_prefix: str = "uc_"


def _split_comment(line: str) -> tuple[str, str]:
    if "!" not in line:
        return line, ""
    i = line.find("!")
    return line[:i], line[i:]


def _translate_identifier_fragment(s: str, opt: TranslateOptions) -> str:
    out: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]

        if ch in GREEK:
            name = GREEK[ch]
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


def translate_text(text: str, opt: TranslateOptions = TranslateOptions()) -> str:
    lines = text.splitlines(keepends=True)
    out_lines: list[str] = []

    bad = reserved_ascii_names()

    for line in lines:
        code, comment = _split_comment(line) if opt.preserve_comments else (line, "")
        new_code = _translate_identifier_fragment(code, opt)

        for name in bad:
            if name in code:
                raise ValueError(
                    f"Identificador ASCII reservado encontrado no fonte unicode: '{name}'. "
                    "Use o símbolo Unicode (ex: α) no .f90u."
                )

        out_lines.append(new_code + comment)

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

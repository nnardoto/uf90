from __future__ import annotations

from pathlib import Path
import json


FORTLS_CONFIG_NAME = ".uf90-fortls.json"


def write_fortls_config(
    root: Path,
    output: Path | None = None,
    extensions: tuple[str, ...] = (".f90u",),
) -> Path:
    """Write a fortls config that indexes Unicode sources, not generated files."""

    root = Path(root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {root}")

    suffixes = tuple(dict.fromkeys(ext.lower() for ext in extensions))
    generated: list[str] = []

    for source in root.rglob("*"):
        if source.is_file() and source.suffix.lower() in suffixes:
            generated.append(source.with_suffix(".f90").relative_to(root).as_posix())

    config = {
        "incl_suffixes": list(suffixes),
        "excl_paths": sorted(generated),
    }

    config_path = Path(output) if output is not None else Path(FORTLS_CONFIG_NAME)
    if not config_path.is_absolute():
        config_path = root / config_path
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return config_path

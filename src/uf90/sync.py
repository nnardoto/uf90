from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from .translator import translate_file, file_sha256, TranslateOptions


@dataclass(frozen=True)
class SyncOptions:
    extensions: tuple[str, ...] = (".f90u",)
    manifest_name: str = ".uf90-manifest.json"
    dry_run: bool = False
    check: bool = False  # se True: não escreve nada, apenas verifica desatualizados
    preserve_comments: bool = True


def _load_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_manifest(path: Path, data: dict[str, str]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def sync_project(root: Path, opt: SyncOptions = SyncOptions()) -> int:
    root = Path(root)
    manifest_path = root / opt.manifest_name
    manifest = _load_manifest(manifest_path)

    changed = 0
    t_opt = TranslateOptions(preserve_comments=opt.preserve_comments)

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in opt.extensions:
            continue

        rel = str(p.relative_to(root))
        sha = file_sha256(p)

        if manifest.get(rel) == sha:
            continue  # não mudou desde a última sync bem-sucedida

        out = p.with_suffix(".f90")
        changed += 1

        if opt.dry_run or opt.check:
            continue

        translate_file(p, out, t_opt)
        manifest[rel] = sha

    if not (opt.dry_run or opt.check):
        _save_manifest(manifest_path, manifest)

    return changed

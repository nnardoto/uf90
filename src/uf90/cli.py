from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from .translator import translate_file, TranslateOptions
from .sync import sync_project, SyncOptions
from . import __version__


def _cmd_sync(ns: argparse.Namespace) -> int:
    exts = (".f90u",) if ns.ext is None else tuple({".f90u", *ns.ext})
    opt = SyncOptions(
        extensions=exts,
        manifest_name=ns.manifest,
        dry_run=ns.dry_run,
        check=ns.check,
        preserve_comments=not ns.no_preserve_comments,
    )
    n = sync_project(ns.root, opt)

    if ns.check:
        if n == 0:
            print("uf90: OK (todos os .f90 estão atualizados)")
            return 0
        print(f"uf90: FAIL ({n} arquivo(s) .f90u mudaram e precisam de sync)")
        return 1

    if ns.dry_run:
        print(f"uf90: dry-run (regeneraria {n} arquivo(s))")
        return 0

    print(f"uf90: synced {n} arquivo(s)")
    return 0


def _cmd_translate(ns: argparse.Namespace) -> int:
    opt = TranslateOptions(preserve_comments=not ns.no_preserve_comments)
    out = translate_file(ns.src, ns.out, opt=opt)
    print(str(out))
    return 0


def _cmd_fpm(ns: argparse.Namespace) -> int:
    fpm = shutil.which("fpm")
    if fpm is None:
        print("uf90 fpm: 'fpm' não encontrado no PATH", file=sys.stderr)
        return 127

    # sempre faz sync (incremental)
    sync_opt = SyncOptions(
        manifest_name=ns.manifest,
        dry_run=False,
        check=False,
        preserve_comments=not ns.no_preserve_comments,
    )
    n = sync_project(ns.root, sync_opt)
    if n:
        print(f"uf90: synced {n} arquivo(s) antes do fpm")

    args = ns.fpm_args if ns.fpm_args else ["--help"]
    print(f"uf90: executando: fpm {' '.join(args)}")
    return subprocess.call([fpm, *args], cwd=str(ns.root))


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="uf90", description="Unicode Fortran workflow (.f90u -> .f90).")
    ap.add_argument("--version", action="version", version=f"uf90 {__version__}")

    sub = ap.add_subparsers(dest="cmd", required=True)

    # sync / check
    sp = sub.add_parser("sync", help="Sincroniza/gera .f90 a partir de .f90u (incremental).")
    sp.add_argument("root", nargs="?", type=Path, default=Path("."))
    sp.add_argument("--manifest", default=".uf90-manifest.json")
    sp.add_argument("--ext", action="append", default=None, help="Extensões adicionais tratadas como Unicode Fortran (repeatable).")
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--check", action="store_true", help="Apenas verifica se está atualizado (exit 1 se não estiver).")
    sp.add_argument("--no-preserve-comments", action="store_true")
    sp.set_defaults(_fn=_cmd_sync)

    spc = sub.add_parser("check", help="Alias de 'uf90 sync --check'.")
    spc.add_argument("root", nargs="?", type=Path, default=Path("."))
    spc.add_argument("--manifest", default=".uf90-manifest.json")
    spc.add_argument("--ext", action="append", default=None)
    spc.add_argument("--no-preserve-comments", action="store_true")
    spc.set_defaults(_fn=_cmd_sync, dry_run=False, check=True)

    # translate
    tp = sub.add_parser("translate", help="Converte um arquivo .f90u em .f90.")
    tp.add_argument("src", type=Path)
    tp.add_argument("-o", "--out", type=Path, default=None)
    tp.add_argument("--no-preserve-comments", action="store_true")
    tp.set_defaults(_fn=_cmd_translate)

    # fpm wrapper
    fp = sub.add_parser("fpm", help="Roda 'sync' e depois chama o fpm com os argumentos fornecidos.")
    fp.add_argument("--root", type=Path, default=Path("."))
    fp.add_argument("--manifest", default=".uf90-manifest.json")
    fp.add_argument("--no-preserve-comments", action="store_true")
    fp.add_argument("fpm_args", nargs=argparse.REMAINDER)
    fp.set_defaults(_fn=_cmd_fpm)

    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    ns = ap.parse_args(argv)
    return ns._fn(ns)


# --- Compatibility entrypoints (opcionais) ---

def main_sync_compat(argv: list[str] | None = None) -> int:
    # mantém o comportamento do binário antigo: uf90-sync [root]
    return main(["sync", *(argv or [])])

def main_translate_compat(argv: list[str] | None = None) -> int:
    return main(["translate", *(argv or [])])

def main_fpm_compat(argv: list[str] | None = None) -> int:
    return main(["fpm", *(argv or [])])


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


def main() -> int:
    root = Path(__file__).resolve().parent
    projects = sorted(path.parent for path in root.glob("*/fpm.toml"))

    fpm = shutil.which("fpm")
    if fpm is None:
        print("examples: fpm não encontrado no PATH", file=sys.stderr)
        return 127

    if shutil.which("fpm-uf90") is None:
        print(
            "examples: plugin fpm-uf90 não encontrado; instale com "
            "'python3 -m pip install -e .'",
            file=sys.stderr,
        )
        return 127

    failures: list[str] = []
    for project in projects:
        print(f"\n=== {project.name} ===", flush=True)
        completed = subprocess.run([fpm, "uf90", "run"], cwd=project)
        if completed.returncode != 0:
            failures.append(project.name)

    if failures:
        print(f"\nFalharam: {', '.join(failures)}", file=sys.stderr)
        return 1

    print(f"\nTodos os {len(projects)} exemplos passaram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

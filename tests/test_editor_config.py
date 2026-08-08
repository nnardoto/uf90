from pathlib import Path
import json

import pytest

import uf90.cli as cli
from uf90.editor import write_fortls_config


def test_fortls_config_includes_unicode_sources_and_excludes_generated_files(
    tmp_path: Path,
):
    (tmp_path / "app").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "app" / "main.f90u").write_text("program main\n", encoding="utf-8")
    (tmp_path / "src" / "physics.f90u").write_text(
        "module physics\n", encoding="utf-8"
    )
    (tmp_path / "src" / "handwritten.f90").write_text(
        "module handwritten\n", encoding="utf-8"
    )

    output = write_fortls_config(tmp_path)

    assert output == tmp_path / ".uf90-fortls.json"
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "incl_suffixes": [".f90u"],
        "excl_paths": ["app/main.f90", "src/physics.f90"],
    }


def test_fortls_config_supports_custom_extensions_and_output(tmp_path: Path):
    (tmp_path / "module.uf90").write_text("module example\n", encoding="utf-8")

    output = write_fortls_config(
        tmp_path,
        Path("config/fortls.json"),
        (".f90u", ".uf90"),
    )

    assert output == tmp_path / "config" / "fortls.json"
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "incl_suffixes": [".f90u", ".uf90"],
        "excl_paths": ["module.f90"],
    }


def test_fortls_config_cli_reports_written_file(tmp_path: Path, capsys):
    (tmp_path / "main.f90u").write_text("program main\n", encoding="utf-8")

    assert cli.main(["fortls-config", str(tmp_path)]) == 0

    output = tmp_path / ".uf90-fortls.json"
    assert capsys.readouterr().out.strip() == str(output)
    assert output.exists()


def test_fortls_config_rejects_a_missing_project_root(tmp_path: Path):
    missing = tmp_path / "missing"

    with pytest.raises(NotADirectoryError, match="Project root is not a directory"):
        write_fortls_config(missing)

    assert not missing.exists()

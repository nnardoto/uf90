import json
from pathlib import Path

from uf90 import cli
from uf90 import editor_setup
from uf90.editor_setup import find_uf90_ls, render_editor_config, write_editor_config


def test_detected_server_path_is_made_absolute(monkeypatch):
    monkeypatch.setattr(
        editor_setup.shutil, "which", lambda executable: "tools/uf90-ls"
    )

    assert Path(find_uf90_ls()).is_absolute()
    assert Path(find_uf90_ls()).parts[-2:] == ("tools", "uf90-ls")


def test_renders_vscode_settings_with_explicit_server():
    rendered = render_editor_config("vscode", "/tools/uf90-ls")
    settings = json.loads(rendered)

    assert settings == {
        "files.associations": {"*.f90u": "FortranFreeForm"},
        "fortran.fortls.path": "/tools/uf90-ls",
        "fortran.fortls.configure": "",
        "fortran.fortls.incrementalSync": False,
        "fortran.fortls.notifyInit": True,
        "fortran.linter.compiler": "Disabled",
    }


def test_renders_neovim_config_and_normalizes_windows_path():
    rendered = render_editor_config("neovim", r"C:\Users\dev\uf90-ls.exe")

    assert "vim.lsp.config('uf90_ls'" in rendered
    assert "vim.lsp.enable('uf90_ls')" in rendered
    assert "C:/Users/dev/uf90-ls.exe" in rendered
    assert "root_markers = { 'fpm.toml', '.git' }" in rendered
    assert "vim.lsp.completion.enable(true" in rendered
    assert "'<C-Space>'" in rendered


def test_cli_prints_config_to_stdout(capsys):
    assert cli.main(
        ["editor-config", "vscode", "--server", "/apps/uf90-ls"]
    ) == 0

    assert json.loads(capsys.readouterr().out)["fortran.fortls.path"] == (
        "/apps/uf90-ls"
    )


def test_write_refuses_existing_file_without_force(tmp_path: Path):
    output = tmp_path / ".vscode" / "settings.json"
    output.parent.mkdir()
    output.write_text('{"editor.tabSize": 2}\n', encoding="utf-8")

    assert cli.main(
        [
            "editor-config",
            "vscode",
            "--server",
            "/apps/uf90-ls",
            "--output",
            str(output),
        ]
    ) == 2
    assert output.read_text(encoding="utf-8") == '{"editor.tabSize": 2}\n'


def test_write_creates_parent_and_force_replaces(tmp_path: Path):
    output = tmp_path / "config" / "uf90.lua"

    assert write_editor_config(
        "neovim", output, server="/apps/uf90-ls"
    ) == output
    assert "/apps/uf90-ls" in output.read_text(encoding="utf-8")

    write_editor_config(
        "neovim", output, server="/new/uf90-ls", force=True
    )
    assert "/new/uf90-ls" in output.read_text(encoding="utf-8")

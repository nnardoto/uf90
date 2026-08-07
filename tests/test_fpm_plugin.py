from pathlib import Path

import uf90.cli as cli


def test_fpm_plugin_syncs_and_forwards_arguments(monkeypatch, tmp_path: Path):
    calls = []

    monkeypatch.setattr(cli.shutil, "which", lambda name: "/usr/local/bin/fpm")
    monkeypatch.setattr(cli, "sync_project", lambda root, options: 2)
    monkeypatch.setattr(
        cli.subprocess,
        "call",
        lambda args, cwd: calls.append((args, cwd)) or 0,
    )

    result = cli.main_fpm_plugin(
        ["--root", str(tmp_path), "build", "--profile", "release"]
    )

    assert result == 0
    assert calls == [
        (["/usr/local/bin/fpm", "build", "--profile", "release"], str(tmp_path))
    ]


def test_compat_entry_point_uses_process_arguments(monkeypatch):
    received = []
    monkeypatch.setattr(cli.sys, "argv", ["uf90-sync", "project", "--check"])
    monkeypatch.setattr(cli, "main", lambda args: received.append(args) or 0)

    assert cli.main_sync_compat() == 0
    assert received == [["sync", "project", "--check"]]


def test_fpm_plugin_without_arguments_shows_help_without_sync(monkeypatch):
    received = []
    monkeypatch.setattr(cli, "main", lambda args: received.append(args) or 0)

    assert cli.main_fpm_plugin([]) == 0
    assert received == [["fpm", "--help"]]


def test_fpm_not_found_returns_127(monkeypatch, tmp_path: Path, capsys):
    monkeypatch.setattr(cli.shutil, "which", lambda name: None)

    result = cli.main_fpm_plugin(["--root", str(tmp_path), "build"])

    assert result == 127
    assert "não encontrado" in capsys.readouterr().err


def test_fpm_exit_status_is_propagated(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(cli.shutil, "which", lambda name: "/usr/local/bin/fpm")
    monkeypatch.setattr(cli, "sync_project", lambda root, options: 0)
    monkeypatch.setattr(cli.subprocess, "call", lambda args, cwd: 42)

    result = cli.main_fpm_plugin(["--root", str(tmp_path), "test"])

    assert result == 42


def test_fpm_defaults_to_help(monkeypatch, tmp_path: Path):
    calls = []
    monkeypatch.setattr(cli.shutil, "which", lambda name: "/usr/local/bin/fpm")
    monkeypatch.setattr(cli, "sync_project", lambda root, options: 0)
    monkeypatch.setattr(
        cli.subprocess,
        "call",
        lambda args, cwd: calls.append((args, cwd)) or 0,
    )

    assert cli.main(["fpm", "--root", str(tmp_path)]) == 0
    assert calls == [(["/usr/local/bin/fpm", "--help"], str(tmp_path))]

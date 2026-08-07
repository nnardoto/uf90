from pathlib import Path
import json

from uf90.sync import sync_project, SyncOptions

def test_check_mode(tmp_path: Path):
    p = tmp_path / "a.f90u"
    p.write_text("real :: α\n", encoding="utf-8")
    # sem manifest: deve acusar 1 pendente
    n = sync_project(tmp_path, SyncOptions(check=True))
    assert n == 1


def test_missing_generated_file_needs_sync(tmp_path: Path):
    p = tmp_path / "a.f90u"
    p.write_text("real :: α\n", encoding="utf-8")
    assert sync_project(tmp_path) == 1

    generated = tmp_path / "a.f90"
    generated.unlink()

    assert sync_project(tmp_path, SyncOptions(check=True)) == 1
    assert sync_project(tmp_path) == 1
    assert generated.read_text(encoding="utf-8") == "real :: uc_alpha\n"


def test_second_sync_is_incremental(tmp_path: Path):
    source = tmp_path / "a.f90u"
    source.write_text("real :: α\n", encoding="utf-8")

    assert sync_project(tmp_path) == 1
    assert sync_project(tmp_path) == 0


def test_source_change_triggers_regeneration(tmp_path: Path):
    source = tmp_path / "a.f90u"
    source.write_text("real :: α\n", encoding="utf-8")
    sync_project(tmp_path)

    source.write_text("real :: β\n", encoding="utf-8")

    assert sync_project(tmp_path) == 1
    assert (tmp_path / "a.f90").read_text(encoding="utf-8") == "real :: uc_beta\n"


def test_dry_run_does_not_create_output_or_manifest(tmp_path: Path):
    source = tmp_path / "a.f90u"
    source.write_text("real :: α\n", encoding="utf-8")

    assert sync_project(tmp_path, SyncOptions(dry_run=True)) == 1
    assert not (tmp_path / "a.f90").exists()
    assert not (tmp_path / ".uf90-manifest.json").exists()


def test_check_does_not_create_output_or_manifest(tmp_path: Path):
    source = tmp_path / "a.f90u"
    source.write_text("real :: α\n", encoding="utf-8")

    assert sync_project(tmp_path, SyncOptions(check=True)) == 1
    assert not (tmp_path / "a.f90").exists()
    assert not (tmp_path / ".uf90-manifest.json").exists()


def test_nested_sources_are_discovered(tmp_path: Path):
    source = tmp_path / "src" / "nested" / "module.f90u"
    source.parent.mkdir(parents=True)
    source.write_text("real :: α\n", encoding="utf-8")

    assert sync_project(tmp_path) == 1
    assert source.with_suffix(".f90").exists()


def test_custom_extension_is_supported(tmp_path: Path):
    source = tmp_path / "module.uf90"
    source.write_text("real :: α\n", encoding="utf-8")
    options = SyncOptions(extensions=(".uf90",))

    assert sync_project(tmp_path, options) == 1
    assert (tmp_path / "module.f90").read_text(encoding="utf-8") == "real :: uc_alpha\n"


def test_malformed_manifest_is_rebuilt(tmp_path: Path):
    source = tmp_path / "a.f90u"
    manifest = tmp_path / ".uf90-manifest.json"
    source.write_text("real :: α\n", encoding="utf-8")
    manifest.write_text("not json", encoding="utf-8")

    assert sync_project(tmp_path) == 1
    saved = json.loads(manifest.read_text(encoding="utf-8"))
    assert "a.f90u" in saved


def test_custom_manifest_name(tmp_path: Path):
    source = tmp_path / "a.f90u"
    source.write_text("real :: α\n", encoding="utf-8")
    options = SyncOptions(manifest_name="cache.json")

    assert sync_project(tmp_path, options) == 1
    assert (tmp_path / "cache.json").exists()


def test_preserve_comments_option_on_first_sync(tmp_path: Path):
    source = tmp_path / "a.f90u"
    source.write_text("! α\n", encoding="utf-8")
    options = SyncOptions(preserve_comments=False)

    assert sync_project(tmp_path, options) == 1
    assert (tmp_path / "a.f90").read_text(encoding="utf-8") == "! uc_alpha\n"

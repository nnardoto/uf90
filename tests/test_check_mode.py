from pathlib import Path
from uf90.sync import sync_project, SyncOptions

def test_check_mode(tmp_path: Path):
    p = tmp_path / "a.f90u"
    p.write_text("real :: α\n", encoding="utf-8")
    # sem manifest: deve acusar 1 pendente
    n = sync_project(tmp_path, SyncOptions(check=True))
    assert n == 1

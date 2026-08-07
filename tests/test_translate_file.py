from pathlib import Path

from uf90.translator import TranslateOptions, file_sha256, translate_file


def test_default_f90u_output_name(tmp_path: Path):
    source = tmp_path / "physics.f90u"
    source.write_text("real :: α\n", encoding="utf-8")

    output = translate_file(source)

    assert output == tmp_path / "physics.f90"
    assert output.read_text(encoding="utf-8") == "real :: uc_alpha\n"


def test_non_f90u_suffix_is_preserved_in_output_name(tmp_path: Path):
    source = tmp_path / "physics.txt"
    source.write_text("real :: α\n", encoding="utf-8")

    output = translate_file(source)

    assert output == tmp_path / "physics.txt.f90"


def test_explicit_output_creates_parent_directories(tmp_path: Path):
    source = tmp_path / "input.f90u"
    output = tmp_path / "generated" / "nested" / "output.f90"
    source.write_text("real :: α\n", encoding="utf-8")

    assert translate_file(source, output) == output
    assert output.read_text(encoding="utf-8") == "real :: uc_alpha\n"


def test_translate_file_option_can_translate_comments(tmp_path: Path):
    source = tmp_path / "comments.f90u"
    source.write_text("! α\n", encoding="utf-8")

    output = translate_file(source, opt=TranslateOptions(preserve_comments=False))

    assert output.read_text(encoding="utf-8") == "! uc_alpha\n"


def test_file_sha256_changes_with_content(tmp_path: Path):
    source = tmp_path / "input.f90u"
    source.write_text("α", encoding="utf-8")
    first = file_sha256(source)
    source.write_text("β", encoding="utf-8")
    second = file_sha256(source)

    assert len(first) == 64
    assert first != second

import pytest

from uf90.translator import translate_with_map


def test_maps_positions_before_inside_and_after_greek_expansion():
    result = translate_with_map("real :: α, x\n")
    source_map = result.source_map

    assert result.text == "real :: uc_alpha, x\n"
    assert source_map.to_generated(0, 8) == (0, 8)
    assert source_map.to_generated(0, 9) == (0, 16)
    assert source_map.to_generated(0, 12) == (0, 19)

    assert source_map.to_source(0, 8) == (0, 8)
    assert source_map.to_source(0, 10) == (0, 8)
    assert source_map.to_source(0, 16) == (0, 9)
    assert source_map.to_source(0, 19) == (0, 12)


def test_maps_each_character_of_subscript_and_superscript_runs():
    result = translate_with_map("T₁₀₀ + c²")
    source_map = result.source_map

    assert result.text == "T_100 + c_p2"
    assert source_map.to_generated(0, 1) == (0, 1)
    assert source_map.to_generated(0, 2) == (0, 3)
    assert source_map.to_generated(0, 3) == (0, 4)
    assert source_map.to_generated(0, 4) == (0, 5)
    assert source_map.to_source(0, 2) == (0, 1)
    assert source_map.to_source(0, 3) == (0, 2)
    assert source_map.to_source(0, 11) == (0, 8)
    assert source_map.to_source(0, 12) == (0, 9)


def test_utf16_positions_include_non_bmp_characters_before_identifier():
    result = translate_with_map('print *, "😀", α\n')
    source_map = result.source_map

    assert source_map.to_generated(0, 15, "utf-16") == (0, 15)
    assert source_map.to_generated(0, 16, "utf-16") == (0, 23)
    assert source_map.to_source(0, 23, "utf-16") == (0, 16)


def test_utf8_and_utf32_position_encodings_are_supported():
    result = translate_with_map("😀 α")

    assert result.source_map.to_generated(0, 5, "utf-8") == (0, 5)
    assert result.source_map.to_generated(0, 3, "utf-32") == (0, 10)
    assert result.source_map.to_source(0, 12, "utf-8") == (0, 5)


def test_map_preserves_empty_logical_line_after_newline():
    result = translate_with_map("α\r\n")

    assert len(result.source_map.lines) == 2
    assert result.source_map.to_generated(1, 0) == (1, 0)


def test_invalid_line_and_encoding_are_rejected():
    source_map = translate_with_map("α").source_map

    with pytest.raises(ValueError, match="line outside"):
        source_map.to_generated(1, 0)
    with pytest.raises(ValueError, match="unsupported position encoding"):
        source_map.to_generated(0, 1, "latin-1")

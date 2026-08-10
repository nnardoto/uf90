import pytest

from uf90.mapping import CALCULUS, GREEK, SUBS, SUPS
from uf90.translator import translate_text


@pytest.mark.parametrize(("symbol", "name"), GREEK.items())
def test_every_greek_letter_at_identifier_start(symbol: str, name: str):
    assert translate_text(symbol) == f"uc_{name.lower()}"


@pytest.mark.parametrize(("symbol", "name"), GREEK.items())
def test_every_greek_letter_inside_identifier(symbol: str, name: str):
    assert translate_text(f"x{symbol}") == f"x{name}"


@pytest.mark.parametrize(
    ("source", "expected"),
    [("∂x", "partial_x"), ("∇φ", "nabla_phi")],
)
def test_calculus_prefixes(source: str, expected: str):
    assert translate_text(source) == expected


def test_every_calculus_symbol_uses_a_readable_prefix():
    for symbol, name in CALCULUS.items():
        assert translate_text(f"{symbol}x") == f"{name}_x"


@pytest.mark.parametrize(("symbol", "replacement"), SUBS.items())
def test_every_subscript(symbol: str, replacement: str):
    assert translate_text(f"x{symbol}") == f"x_{replacement}"


@pytest.mark.parametrize(("symbol", "replacement"), SUPS.items())
def test_every_superscript(symbol: str, replacement: str):
    assert translate_text(f"x{symbol}") == f"x_p{replacement}"


def test_mixed_subscript_sequence_gets_one_separator():
    assert translate_text("tensorᵢⱼ₁₀") == "tensor_ij10"


def test_separate_subscript_runs_get_separate_separators():
    assert translate_text("x₁+y₂") == "x_1+y_2"

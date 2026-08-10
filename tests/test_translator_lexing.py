import pytest

from uf90.translator import TranslateOptions, translate_text


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('print *, "α", α\n', 'print *, "α", uc_alpha\n'),
        ("print *, 'β', β\n", "print *, 'β', uc_beta\n"),
        ("print *, 'α! β', γ\n", "print *, 'α! β', uc_gamma\n"),
        ("print *, 'it''s α', α\n", "print *, 'it''s α', uc_alpha\n"),
        ('print *, "a ""quoted"" α", α\n', 'print *, "a ""quoted"" α", uc_alpha\n'),
        ("real :: α ! β\n", "real :: uc_alpha ! β\n"),
        ("obj%μ = obj%σ²\n", "obj%uc_mu = obj%uc_sigma_p2\n"),
        ("real :: Aᵢⱼ, vₙ₁\n", "real :: A_ij, v_n1\n"),
        ("real :: α", "real :: uc_alpha"),
        ("real :: α\r\n", "real :: uc_alpha\r\n"),
    ],
)
def test_lexical_contexts(source: str, expected: str):
    assert translate_text(source) == expected


def test_continued_double_quoted_literal():
    source = 'character(*) :: s = "α &\n  &β", γ\n'
    expected = 'character(*) :: s = "α &\n  &β", uc_gamma\n'
    assert translate_text(source) == expected


def test_continued_single_quoted_literal():
    source = "character(*) :: s = 'α &\n  &β', γ\n"
    expected = "character(*) :: s = 'α &\n  &β', uc_gamma\n"
    assert translate_text(source) == expected


def test_can_translate_unicode_inside_comments_when_requested():
    source = "real :: α ! β₁\n"
    options = TranslateOptions(preserve_comments=False)
    assert translate_text(source, options) == "real :: uc_alpha ! uc_beta_1\n"


def test_reserved_name_in_code_is_rejected():
    with pytest.raises(ValueError, match="uc_alpha"):
        translate_text("real :: uc_alpha\n")


@pytest.mark.parametrize("name", ["partial_x", "nabla_phi"])
def test_reserved_calculus_prefix_in_code_is_rejected(name: str):
    with pytest.raises(ValueError, match=name):
        translate_text(f"real :: {name}\n")


def test_reserved_name_in_string_and_comment_is_allowed():
    source = 'print *, "uc_alpha" ! uc_beta\n'
    assert translate_text(source) == source


def test_reserved_name_must_match_complete_identifier():
    source = "real :: my_uc_alpha_value\n"
    assert translate_text(source) == source


def test_reserved_calculus_prefix_must_start_identifier():
    source = "real :: my_partial_x, my_nabla_phi\n"
    assert translate_text(source) == source


def test_empty_input():
    assert translate_text("") == ""

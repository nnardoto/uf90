from uf90.translator import translate_text

def test_translate_greek_and_sub_sup():
    src = "real :: α, Δt, T₁₀₀, c²\n"
    out = translate_text(src)
    assert "uc_alpha" in out
    assert "uc_delta" in out
    assert "T_100" in out
    assert "c_p2" in out


def test_translate_alphanumeric_subscripts():
    src = "real :: Eₙ, Aᵢⱼ, vₙ₁, xᵦ\n"
    out = translate_text(src)
    assert out == "real :: E_n, A_ij, v_n1, x_beta\n"


def test_translate_available_latin_subscript_alphabet():
    src = "real :: qₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ\n"
    out = translate_text(src)
    assert out == "real :: q_aehijklmnoprstuvx\n"


def test_preserves_character_literals_and_comments():
    src = 'print *, "α!", α ! β permanece no comentário\n'
    out = translate_text(src)
    assert out == 'print *, "α!", uc_alpha ! β permanece no comentário\n'


def test_preserves_continued_character_literal():
    src = 'print *, "α &\n& β", γ\n'
    out = translate_text(src)
    assert out == 'print *, "α &\n& β", uc_gamma\n'


def test_reserved_name_inside_string_is_allowed():
    src = 'print *, "uc_alpha"\n'
    assert translate_text(src) == src

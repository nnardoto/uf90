from uf90.translator import translate_text

def test_translate_greek_and_sub_sup():
    src = "real :: α, Δt, T₁₀₀, c²\n"
    out = translate_text(src)
    assert "uc_alpha" in out
    assert "uc_delta" in out
    assert "T_100" in out
    assert "c_p2" in out

from uf90.translator import translate_text

def test_atomnumber_does_not_trigger_reserved():
    # Regression: 'AtomNumber' contains substring 'Nu' but must not error.
    src = "type :: AtomNumber\nend type AtomNumber\n"
    out = translate_text(src)
    assert "AtomNumber" in out

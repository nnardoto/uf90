from __future__ import annotations

GREEK = {
    # lowercase
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon",
    "ζ": "zeta", "η": "eta", "θ": "theta", "ι": "iota", "κ": "kappa",
    "λ": "lambda", "μ": "mu", "ν": "nu", "ξ": "xi", "ο": "omicron",
    "π": "pi", "ρ": "rho", "σ": "sigma", "τ": "tau", "υ": "upsilon",
    "φ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega",
    # uppercase
    "Α": "Alpha", "Β": "Beta", "Γ": "Gamma", "Δ": "Delta", "Ε": "Epsilon",
    "Ζ": "Zeta", "Η": "Eta", "Θ": "Theta", "Ι": "Iota", "Κ": "Kappa",
    "Λ": "Lambda", "Μ": "Mu", "Ν": "Nu", "Ξ": "Xi", "Ο": "Omicron",
    "Π": "Pi", "Ρ": "Rho", "Σ": "Sigma", "Τ": "Tau", "Υ": "Upsilon",
    "Φ": "Phi", "Χ": "Chi", "Ψ": "Psi", "Ω": "Omega",
}

CALCULUS = {
    "∂": "partial",
    "∇": "nabla",
}

SUBS = {
    # digits
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
    # Latin letters for which Unicode defines a subscript character. Unicode
    # does not provide a complete subscript alphabet (there is no Latin b, c,
    # d, f, g, q, w, y or z, for example).
    "ₐ": "a", "ₑ": "e", "ₔ": "schwa", "ₕ": "h", "ᵢ": "i", "ⱼ": "j",
    "ₖ": "k", "ₗ": "l", "ₘ": "m", "ₙ": "n", "ₒ": "o",
    "ₚ": "p", "ᵣ": "r", "ₛ": "s", "ₜ": "t", "ᵤ": "u",
    "ᵥ": "v", "ₓ": "x",
    # Scientific notation also commonly uses the available Greek subscript
    # modifier letters.
    "ᵦ": "beta", "ᵧ": "gamma", "ᵨ": "rho", "ᵩ": "phi", "ᵪ": "chi",
}

SUPS = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
}

def is_fortran_ident_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_"

def reserved_ascii_names() -> set[str]:
    # Reservamos APENAS os identificadores que o uf90 gera diretamente quando um
    # identificador "começa" com símbolo grego (ex.: α -> uc_alpha).
    # Isso evita falsos positivos como "AtomNumber" conter "Nu" como substring.
    base = {x.lower() for x in GREEK.values()}
    return {f"uc_{x}" for x in base}


def reserved_ascii_prefixes() -> set[str]:
    return {f"{name}_" for name in CALCULUS.values()}

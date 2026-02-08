-- Snippets para inserção de símbolos Unicode em Fortran
-- Para usar com LuaSnip no Neovim
-- 
-- Instalação:
-- 1. Certifique-se de ter LuaSnip instalado
-- 2. Coloque este arquivo em: ~/.config/nvim/luasnippets/f90u.lua
--    (ou f90u.lua para usar também com .f90u)
-- 3. Os snippets estarão disponíveis ao editar arquivos .f90u ou .f90u

local ls = require("luasnip")
local s = ls.snippet
local t = ls.text_node
local i = ls.insert_node

return {
  -- LETRAS GREGAS MINÚSCULAS
  s("alpha", { t("α") }),
  s("beta", { t("β") }),
  s("gamma", { t("γ") }),
  s("delta", { t("δ") }),
  s("epsilon", { t("ε") }),
  s("zeta", { t("ζ") }),
  s("eta", { t("η") }),
  s("theta", { t("θ") }),
  s("iota", { t("ι") }),
  s("kappa", { t("κ") }),
  s("lambda", { t("λ") }),
  s("mu", { t("μ") }),
  s("nu", { t("ν") }),
  s("xi", { t("ξ") }),
  s("omicron", { t("ο") }),
  s("pi", { t("π") }),
  s("rho", { t("ρ") }),
  s("sigma", { t("σ") }),
  s("tau", { t("τ") }),
  s("upsilon", { t("υ") }),
  s("phi", { t("φ") }),
  s("chi", { t("χ") }),
  s("psi", { t("ψ") }),
  s("omega", { t("ω") }),

  -- LETRAS GREGAS MAIÚSCULAS
  s("Alpha", { t("Α") }),
  s("Beta", { t("Β") }),
  s("Gamma", { t("Γ") }),
  s("Delta", { t("Δ") }),
  s("Epsilon", { t("Ε") }),
  s("Zeta", { t("Ζ") }),
  s("Eta", { t("Η") }),
  s("Theta", { t("Θ") }),
  s("Iota", { t("Ι") }),
  s("Kappa", { t("Κ") }),
  s("Lambda", { t("Λ") }),
  s("Mu", { t("Μ") }),
  s("Nu", { t("Ν") }),
  s("Xi", { t("Ξ") }),
  s("Omicron", { t("Ο") }),
  s("Pi", { t("Π") }),
  s("Rho", { t("Ρ") }),
  s("Sigma", { t("Σ") }),
  s("Tau", { t("Τ") }),
  s("Upsilon", { t("Υ") }),
  s("Phi", { t("Φ") }),
  s("Chi", { t("Χ") }),
  s("Psi", { t("Ψ") }),
  s("Omega", { t("Ω") }),

  -- SUBSCRITOS (0-9)
  s("_0", { t("₀") }),
  s("_1", { t("₁") }),
  s("_2", { t("₂") }),
  s("_3", { t("₃") }),
  s("_4", { t("₄") }),
  s("_5", { t("₅") }),
  s("_6", { t("₆") }),
  s("_7", { t("₇") }),
  s("_8", { t("₈") }),
  s("_9", { t("₉") }),

  -- SOBRESCRITOS (0-9)
  s("^0", { t("⁰") }),
  s("^1", { t("¹") }),
  s("^2", { t("²") }),
  s("^3", { t("³") }),
  s("^4", { t("⁴") }),
  s("^5", { t("⁵") }),
  s("^6", { t("⁶") }),
  s("^7", { t("⁷") }),
  s("^8", { t("⁸") }),
  s("^9", { t("⁹") }),

  -- EXEMPLOS COMPOSTOS COMUNS
  s("Dt", { t("Δt") }),  -- Delta t
  s("DT", { t("ΔT") }),  -- Delta T maiúsculo
  s("c2", { t("c²") }),  -- c ao quadrado
  s("x0", { t("x₀") }),  -- x índice 0
  s("v0", { t("v₀") }),  -- v índice 0
  s("T0", { t("T₀") }),  -- T índice 0
  
  -- EXEMPLOS FÍSICOS COMUNS
  s("emc2", {            -- E = mc²
    t("E = m * c²")
  }),
  
  s("angulo", {          -- Variável de ângulo com α, β, θ
    t("α")
  }),
}

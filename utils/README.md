# Perfis de Editor para uf90 - Unicode Fortran

Este repositório contém perfis de snippets para facilitar a inserção de símbolos Unicode ao escrever código Fortran usando o [uf90](https://github.com/nnardoto/uf90).

## 📋 Conteúdo

- `fortran-unicode.lua` - Snippets para Neovim (LuaSnip)
- `fortran-unicode.code-snippets` - Snippets para VSCode

## 🎯 Símbolos Suportados

### Letras Gregas Minúsculas
`alpha` → α, `beta` → β, `gamma` → γ, `delta` → δ, `epsilon` → ε, `zeta` → ζ, `eta` → η, `theta` → θ, `iota` → ι, `kappa` → κ, `lambda` → λ, `mu` → μ, `nu` → ν, `xi` → ξ, `omicron` → ο, `pi` → π, `rho` → ρ, `sigma` → σ, `tau` → τ, `upsilon` → υ, `phi` → φ, `chi` → χ, `psi` → ψ, `omega` → ω

### Letras Gregas Maiúsculas
`Alpha` → Α, `Beta` → Β, `Gamma` → Γ, `Delta` → Δ, etc.

### Subscritos
`_0` → ₀, `_1` → ₁, `_2` → ₂, ..., `_9` → ₉

### Sobrescritos
`^0` → ⁰, `^1` → ¹, `^2` → ², ..., `^9` → ⁹

### Compostos Comuns
- `Dt` → Δt (intervalo de tempo)
- `DT` → ΔT (variação de temperatura)
- `c2` → c² (c ao quadrado)
- `x0` → x₀ (x índice 0)
- `v0` → v₀ (velocidade inicial)
- `emc2` → E = m * c² (equação de Einstein)

## 🚀 Instalação

### Neovim (com LuaSnip)

#### Pré-requisitos
- Neovim 0.7+
- Plugin [LuaSnip](https://github.com/L3MON4D3/LuaSnip) instalado

#### Instalação

1. **Criar diretório para snippets Lua:**
```bash
mkdir -p ~/.config/nvim/luasnippets
```

2. **Copiar arquivo de snippets:**
```bash
cp fortran-unicode.lua ~/.config/nvim/luasnippets/f90u.lua
```

3. **Configurar LuaSnip** no seu `init.lua` ou `init.vim`:

**Para init.lua:**
```lua
-- Configurar LuaSnip para carregar snippets Lua
require("luasnip.loaders.from_lua").load({paths = "~/.config/nvim/luasnippets"})

-- Opcional: keybindings para navegação nos snippets
vim.keymap.set({"i", "s"}, "<Tab>", function()
  if require("luasnip").expand_or_jumpable() then
    require("luasnip").expand_or_jump()
  else
    return "<Tab>"
  end
end, {expr = true})

vim.keymap.set({"i", "s"}, "<S-Tab>", function()
  if require("luasnip").jumpable(-1) then
    require("luasnip").jump(-1)
  end
end)
```

**Para init.vim:**
```vim
" Configurar LuaSnip para carregar snippets Lua
lua << EOF
require("luasnip.loaders.from_lua").load({paths = "~/.config/nvim/luasnippets"})
EOF

" Opcional: keybindings para navegação nos snippets
imap <silent><expr> <Tab> luasnip#expand_or_jumpable() ? '<Plug>luasnip-expand-or-jump' : '<Tab>'
smap <silent><expr> <Tab> luasnip#expand_or_jumpable() ? '<Plug>luasnip-expand-or-jump' : '<Tab>'
imap <silent><expr> <S-Tab> luasnip#jumpable(-1) ? '<Plug>luasnip-jump-prev' : '<S-Tab>'
smap <silent><expr> <S-Tab> luasnip#jumpable(-1) ? '<Plug>luasnip-jump-prev' : '<S-Tab>'
```

4. **Aplicar associação de arquivo** (adicione ao seu `init.lua` ou `init.vim`):

**init.lua:**
```lua
-- Reconhecer .f90u como Fortran
vim.filetype.add({
  extension = {
    f90u = 'fortran',
  }
})
```

**init.vim:**
```vim
" Reconhecer .f90u como Fortran
autocmd BufRead,BufNewFile *.f90u set filetype=fortran
```

5. **Reiniciar Neovim** ou executar `:source $MYVIMRC`

#### Uso no Neovim

1. Abra um arquivo `.f90u`
2. Digite o trigger (ex: `alpha`) e pressione `Tab`
3. O símbolo Unicode (α) será inserido

**Exemplo:**
```fortran
! Digite: alpha<Tab>
! Resultado: α

real :: alpha<Tab>, beta<Tab>  ! real :: α, β
```

### VSCode

#### Instalação

1. **Abrir pasta de snippets do usuário:**
   - Pressione `Ctrl+Shift+P` (ou `Cmd+Shift+P` no Mac)
   - Digite: `Preferences: Configure User Snippets`
   - Selecione: `New Global Snippets file...`
   - Nome: `fortran-unicode`

2. **Copiar conteúdo:**
   - Abra o arquivo `fortran-unicode.code-snippets`
   - Copie todo o conteúdo
   - Cole no arquivo criado no passo anterior

**OU**

1. **Copiar diretamente para a pasta de snippets:**

**Linux/Mac:**
```bash
mkdir -p ~/.config/Code/User/snippets
cp fortran-unicode.code-snippets ~/.config/Code/User/snippets/
```

**Windows:**
```powershell
mkdir $env:APPDATA\Code\User\snippets
copy fortran-unicode.code-snippets $env:APPDATA\Code\User\snippets\
```

2. **Configurar associação de arquivo** (opcional):

Adicione ao seu `settings.json` (Ctrl+Shift+P → `Preferences: Open Settings (JSON)`):
```json
{
  "files.associations": {
    "*.f90u": "fortran"
  }
}
```

#### Uso no VSCode

1. Abra um arquivo `.f90u`
2. Digite o trigger (ex: `alpha`)
3. Selecione o snippet no menu de autocomplete (ou pressione Tab/Enter)
4. O símbolo Unicode (α) será inserido

**Exemplo:**
```fortran
! Digite: alpha
! Aparece menu: α
! Pressione Enter
! Resultado: α

real :: alpha, beta  ! Use autocomplete para inserir α, β
```

#### Dica VSCode
Para ver todos os snippets disponíveis, pressione `Ctrl+Space` em qualquer lugar do arquivo.

## 📝 Exemplos de Uso

### Exemplo 1: Declaração de Variáveis Físicas
```fortran
program physics
  implicit none
  
  ! Digite os triggers seguidos de Tab/Enter:
  ! alpha, beta, gamma, Delta, Dt
  real :: α, β, γ     ! Ângulos
  real :: Δ, Δt       ! Variações
  real :: π = 3.14159
  
  ! Velocidades com índices
  ! v, _0, v, _1
  real :: v₀, v₁
  
  ! Energia
  ! E, c, ^2
  real :: E, m, c²
  
  c² = 299792458.0**2
  E = m * c²
end program physics
```

### Exemplo 2: Equações Diferenciais
```fortran
subroutine solve_ode(t, y, dydt)
  real, intent(in) :: t
  real, dimension(:), intent(in) :: y
  real, dimension(:), intent(out) :: dydt
  
  ! Parâmetros: alpha, beta, gamma
  real :: α = 0.1, β = 0.2, γ = 0.3
  
  ! dy/dt
  dydt(1) = α * y(1)
  dydt(2) = β * y(2) - γ * y(1) * y(2)
end subroutine
```

### Exemplo 3: Mecânica Quântica
```fortran
module quantum
  implicit none
  
  ! Psi (função de onda), Phi (fase)
  complex :: Ψ, Φ
  
  ! hbar (constante de Planck reduzida)
  real :: ℏ = 1.054571817e-34
  
  ! Lambda (comprimento de onda)
  real :: λ
  
contains
  subroutine schrodinger()
    ! Operador Hamiltoniano
    ! ... implementação ...
  end subroutine
end module
```

## 🔧 Customização

### Adicionar Novos Símbolos

#### Neovim (LuaSnip)
Edite `~/.config/nvim/luasnippets/f90u.lua` e adicione:
```lua
  s("new_symbol", { t("🔬") }),
```

#### VSCode
Edite o arquivo de snippets e adicione:
```json
  "New Symbol": {
    "prefix": "new_symbol",
    "body": "🔬",
    "description": "Descrição do símbolo"
  },
```

### Modificar Triggers Existentes

Basta editar o campo `prefix` (VSCode) ou o primeiro argumento de `s()` (Neovim).

## 🐛 Troubleshooting

### Neovim

**Problema:** Snippets não aparecem
- Verifique se LuaSnip está instalado: `:lua print(vim.inspect(require('luasnip')))`
- Verifique o caminho: `:lua print(vim.fn.stdpath('config') .. '/luasnippets')`
- Certifique-se que o arquivo está em `luasnippets/f90u.lua`

**Problema:** Tab não expande snippets
- Verifique se os keybindings estão configurados
- Tente usar `Ctrl+K` para expandir manualmente

### VSCode

**Problema:** Snippets não aparecem
- Verifique em: File → Preferences → User Snippets
- Certifique-se que o arquivo JSON é válido (sem vírgulas extras)
- Reinicie o VSCode

**Problema:** Autocomplete não mostra símbolos Unicode
- Vá em Settings → Text Editor → Suggestions
- Habilite "Show Snippets"

## 📚 Referências

- [uf90 - Unicode Fortran Translator](https://github.com/nnardoto/uf90)
- [LuaSnip Documentation](https://github.com/L3MON4D3/LuaSnip)
- [VSCode Snippets Guide](https://code.visualstudio.com/docs/editor/userdefinedsnippets)

## 🤝 Contribuindo

Contribuições são bem-vindas! Para adicionar novos símbolos ou melhorar os snippets:

1. Fork este repositório
2. Adicione seus símbolos em ambos os arquivos (Neovim e VSCode)
3. Teste as mudanças
4. Envie um Pull Request

## 📄 Licença

MIT License - use livremente!

## ✨ Agradecimentos

- Projeto [uf90](https://github.com/nnardoto/uf90) por tornar Unicode em Fortran possível
- Comunidade Fortran por manter a linguagem viva e moderna

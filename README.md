# uf90 (Python)

`uf90` é uma ferramenta em **Python** para trabalhar com “Unicode Fortran”:
você escreve seus fontes com símbolos Unicode (ex.: `α`, `Δt`, `T₁₀₀`, `c²`) em arquivos
`*.f90u` e o `uf90` gera automaticamente os arquivos `*.f90` equivalentes (ASCII-safe),
prontos para compilação (por exemplo com `fpm`).

A proposta é simples:

- **Você edita:** `*.f90u`
- **Você compila/executa:** `*.f90` (gerado)
- **Automação:** `uf90 sync` (incremental) e `uf90 fpm ...` (wrapper)

---

## Status do projeto

- Implementação oficial: **Python**
- CLI idiomático: `uf90 <subcomando>`
- Mantém um **manifest/cache** (`.uf90-manifest.json`) para sincronização incremental

---

## Instalação

### Opção A — Desenvolvimento local (recomendado no repo)
Na raiz do repositório (onde está o `pyproject.toml`):

```bash
python3 -m pip install -e .


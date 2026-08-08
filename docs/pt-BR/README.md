# uf90: notação matemática Unicode para Fortran portátil

[English](../../README.md)

`uf90` permite escrever identificadores matemáticos Unicode em projetos
Fortran. Ele traduz arquivos `*.f90u` para arquivos `*.f90` ASCII comuns, que
são então compilados pelo `fpm` e pelo compilador Fortran existente.

O projeto está em estágio inicial (`0.1.x`). Ele é um tradutor fonte-a-fonte,
não um compilador ou uma extensão da linguagem Fortran.

## Começando com fpm

Instale a versão publicada no [PyPI](https://pypi.org/project/uf90/) usando
`pipx`:

```bash
pipx install uf90
```

Se o terminal não encontrar `uf90` ou `fpm-uf90` depois da instalação, execute
`pipx ensurepath` e abra um novo terminal.

A instalação fornece o comando `uf90` e o plugin `fpm-uf90`. Com ambos `fpm` e
`fpm-uf90` disponíveis no `PATH`, execute o plugin dentro de um projeto que
contenha um arquivo `fpm.toml`:

```bash
fpm uf90 build
fpm uf90 run
fpm uf90 test
```

O plugin procura arquivos `*.f90u` no projeto, atualiza os respectivos arquivos
`*.f90` e encaminha o comando para o `fpm`. Argumentos adicionais também são
encaminhados:

```bash
fpm uf90 build --profile release
```

Na prática, isto:

```bash
fpm uf90 build
```

equivale a:

```bash
uf90 sync
fpm build
```

## Exemplo mínimo

Escreva os fontes nas pastas reconhecidas pelo `fpm`, usando a extensão
`.f90u`. Este exemplo rotaciona o ponto `(x₀, y₀)` por um ângulo `θ` e armazena
o resultado em `(x₁, y₁)`:

```fortran
! app/main.f90u
program rotation
  implicit none
  real :: π, θ
  real :: x₀, y₀, x₁, y₁

  π = acos(-1.0)
  θ = π / 4.0

  x₀ = 1.0
  y₀ = 0.0

  x₁ = cos(θ) * x₀ - sin(θ) * y₀
  y₁ = sin(θ) * x₀ + cos(θ) * y₀

  print *, x₁, y₁
end program rotation
```

Ao executar `fpm uf90 run`, o `uf90` gera:

```fortran
! app/main.f90
program rotation
  implicit none
  real :: uc_pi, uc_theta
  real :: x_0, y_0, x_1, y_1

  uc_pi = acos(-1.0)
  uc_theta = uc_pi / 4.0

  x_0 = 1.0
  y_0 = 0.0

  x_1 = cos(uc_theta) * x_0 - sin(uc_theta) * y_0
  y_1 = sin(uc_theta) * x_0 + cos(uc_theta) * y_0

  print *, x_1, y_1
end program rotation
```

Strings e comentários são preservados. O arquivo `.f90` é uma saída gerada;
edite o fonte `.f90u` correspondente.

## Notação reconhecida

- letras gregas: `α` → `uc_alpha`, `Δt` → `uc_deltat`;
- subscritos numéricos: `T₁₀₀` → `T_100`;
- subscritos alfanuméricos: `Eₙ` → `E_n`, `Aᵢⱼ` → `A_ij`;
- sobrescritos: `c²` → `c_p2`.

O Unicode não oferece versões subscritas de todas as letras. O conjunto atual
inclui `ₐ ₑ ₕ ᵢ ⱼ ₖ ₗ ₘ ₙ ₒ ₚ ᵣ ₛ ₜ ᵤ ᵥ ₓ`, `ₔ`, dígitos e as formas gregas
`ᵦ ᵧ ᵨ ᵩ ᵪ`.

## Comandos sem fpm

Para uso direto ou integração com outros fluxos:

```bash
uf90 sync [diretório]
uf90 check [diretório]
uf90 translate arquivo.f90u [-o arquivo.f90]
```

`uf90 sync` usa `.uf90-manifest.json` como cache incremental. `uf90 check` não
modifica arquivos e retorna status diferente de zero quando alguma saída
precisa ser atualizada.

## Estado e escopo

A versão atual é destinada à experimentação da notação em projetos `fpm` e à
identificação de casos de tradução ainda não cobertos. A interface e o
mapeamento podem mudar enquanto o projeto permanecer abaixo da versão `1.0`.

O `uf90` atualmente:

- traduz identificadores sem alterar texto dentro de strings e comentários;
- gera Fortran ASCII que continua pelo fluxo normal do `fpm`;
- executa testes automatizados em Linux, macOS e Windows com Python 3.10 a
  3.14.

Ele não valida a semântica do programa, não substitui o compilador Fortran e
não depende de LLVM ou MLIR.

## Exemplos e desenvolvimento

A pasta [`examples`](../../examples/) contém seis projetos `fpm` progressivos.
Para executá-los a partir de um clone do repositório:

```bash
python3 -m pip install -e '.[test]'
python3 -m pytest
python3 examples/run_all.py
```

O procedimento usado pelos mantenedores para publicar novas versões está em
[`docs/RELEASING.md`](../RELEASING.md).

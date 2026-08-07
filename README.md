# uf90

`uf90` traduz identificadores matemáticos escritos em arquivos `*.f90u` para
Fortran ASCII portátil. O resultado é um arquivo `*.f90` comum, compilável com
`fpm` e compiladores Fortran existentes.

```fortran
! src/physics.f90u
program physics
  real :: α, Δt, T₁₀₀, c²
  print *, "α =", α
end program physics
```

gera:

```fortran
! src/physics.f90
program physics
  real :: uc_alpha, uc_deltat, T_100, c_p2
  print *, "α =", uc_alpha
end program physics
```

Strings e comentários são preservados por padrão.

## Instalação para desenvolvimento

```bash
python3 -m pip install -e .
```

A instalação fornece o comando `uf90` e o plugin `fpm-uf90`. O `fpm`
descobre plugins pelo padrão de executáveis `fpm-<nome>`; com o diretório de
scripts do Python no `PATH`, o plugin pode ser chamado como `fpm uf90`.

## Uso com fpm

Em um projeto que contenha `fpm.toml` e fontes `*.f90u`:

```bash
fpm uf90 build
fpm uf90 run
fpm uf90 test
fpm uf90 install --prefix ~/.local
```

O plugin executa duas etapas:

1. sincroniza recursivamente os arquivos `*.f90u` com os respectivos `*.f90`;
2. encaminha o comando e seus argumentos para o executável `fpm` instalado.

Por exemplo, `fpm uf90 build --profile release` equivale a:

```bash
uf90 sync
fpm build --profile release
```

O comando antigo continua disponível para compatibilidade:

```bash
uf90 fpm build
fpm-unicode build
```

## Comandos diretos

```bash
uf90 sync [diretório]
uf90 check [diretório]
uf90 translate arquivo.f90u [-o arquivo.f90]
uf90 fpm <comando-fpm> [argumentos]
```

`uf90 sync` mantém o cache incremental `.uf90-manifest.json`. `uf90 check`
não modifica arquivos e retorna status 1 quando alguma saída precisa ser
regenerada.

## Exemplos executáveis

A pasta [`examples`](examples/) contém seis projetos `fpm` progressivos, de
escalares a uma simulação numérica multifonte. Para traduzir, compilar e
executar todos:

```bash
python3 examples/run_all.py
```

## Mapeamento atual

- letras gregas: `α` → `uc_alpha`, `Δt` → `uc_deltat`;
- subscritos numéricos: `T₁₀₀` → `T_100`;
- subscritos alfanuméricos: `Eₙ` → `E_n`, `Aᵢⱼ` → `A_ij`,
  `vₙ₁` → `v_n1`;
- sobrescritos: `c²` → `c_p2`.

O Unicode não define uma forma subscrita para todas as letras. O `uf90`
aceita as formas latinas disponíveis `ₐ ₑ ₕ ᵢ ⱼ ₖ ₗ ₘ ₙ ₒ ₚ ᵣ ₛ ₜ ᵤ ᵥ ₓ`, além de
`ₔ` (schwa), dos dígitos e das variantes gregas `ᵦ ᵧ ᵨ ᵩ ᵪ`.

Nesta etapa o projeto é deliberadamente um tradutor fonte-a-fonte. Ele não
introduz semântica nova na linguagem e não depende de LLVM, MLIR ou de um
compilador específico.

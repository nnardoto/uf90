# uf90: Unicode mathematical notation for portable Fortran

[![PyPI](https://img.shields.io/pypi/v/uf90.svg)](https://pypi.org/project/uf90/)
[![CI](https://github.com/nnardoto/uf90/actions/workflows/ci.yml/badge.svg)](https://github.com/nnardoto/uf90/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/uf90.svg)](https://pypi.org/project/uf90/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[Português (Brasil)](https://github.com/nnardoto/uf90/blob/main/docs/pt-BR/README.md)

`uf90` lets you write mathematical Unicode identifiers in Fortran projects.
It translates `*.f90u` files into ordinary ASCII `*.f90` files, which are then
compiled by `fpm` and your existing Fortran compiler.

The project is at an early stage (`0.1.x`). It is a source-to-source translator,
not a compiler or a Fortran language extension.

## Quick start with fpm

Install the version published on [PyPI](https://pypi.org/project/uf90/) with
`pipx`:

```bash
pipx install uf90
```

If your shell cannot find `uf90` or `fpm-uf90` after installation, run
`pipx ensurepath` and open a new terminal.

The installation provides both the `uf90` command and the `fpm-uf90` plugin.
With `fpm` and `fpm-uf90` available on `PATH`, run the plugin from a project
containing an `fpm.toml` file:

```bash
fpm uf90 build
fpm uf90 run
fpm uf90 test
```

The plugin finds `*.f90u` files in the project, updates their corresponding
`*.f90` files, and forwards the command to `fpm`. Additional arguments are
forwarded as well:

```bash
fpm uf90 build --profile release
```

In practice, this:

```bash
fpm uf90 build
```

is equivalent to:

```bash
uf90 sync
fpm build
```

## Minimal example

Write source files in the directories recognized by `fpm`, using the `.f90u`
extension. This example rotates the point `(x₀, y₀)` by an angle `θ` and stores
the result in `(x₁, y₁)`:

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

Running `fpm uf90 run` generates:

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

Strings and comments are preserved. The `.f90` file is generated output; edit
the corresponding `.f90u` source instead.

## Supported notation

- Greek letters: `α` → `uc_alpha`, `Δt` → `uc_deltat`;
- numeric subscripts: `T₁₀₀` → `T_100`;
- alphanumeric subscripts: `Eₙ` → `E_n`, `Aᵢⱼ` → `A_ij`;
- superscripts: `c²` → `c_p2`.

Unicode does not provide subscript forms for every letter. The current set
includes `ₐ ₑ ₕ ᵢ ⱼ ₖ ₗ ₘ ₙ ₒ ₚ ᵣ ₛ ₜ ᵤ ᵥ ₓ`, `ₔ`, digits, and the Greek forms
`ᵦ ᵧ ᵨ ᵩ ᵪ`.

## Commands without fpm

For direct use or integration with other workflows:

```bash
uf90 sync [directory]
uf90 check [directory]
uf90 translate source.f90u [-o source.f90]
```

`uf90 sync` uses `.uf90-manifest.json` as an incremental cache. `uf90 check`
does not modify files and returns a non-zero status when generated output needs
to be updated.

## Project status and scope

The current version is intended for experimenting with the notation in `fpm`
projects and for finding translation cases that are not covered yet. The
interface and mappings may change while the project remains below version
`1.0`.

`uf90` currently:

- translates identifiers without changing text inside strings and comments;
- generates ASCII Fortran that continues through the regular `fpm` workflow;
- runs automated tests on Linux, macOS, and Windows with Python 3.10 through
  3.14.

It does not validate program semantics, replace the Fortran compiler, or depend
on LLVM or MLIR.

## Examples and development

The [`examples`](https://github.com/nnardoto/uf90/tree/main/examples) directory
contains six progressive `fpm` projects. To run them from a repository clone:

```bash
python3 -m pip install -e '.[test]'
python3 -m pytest
python3 examples/run_all.py
```

The maintainer release procedure is documented in
[`docs/RELEASING.md`](https://github.com/nnardoto/uf90/blob/main/docs/RELEASING.md).

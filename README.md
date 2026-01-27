uf90: A Small Helper for Writing Readable Fortran Code
=====================================================

uf90 is a small helper tool for writing Fortran code with improved readability for mathematical expressions.

Source files are written as `.uf90`, where a limited and explicit set of Unicode symbols (mainly Greek letters and the Δ operator) is allowed.  
Before compilation, `.uf90` files are translated into standard `.f90` files.

Only standard Fortran is passed to the compiler.

_This package is not intended to be an advanced solution, but it may be useful for someone._

---

How it works
------------

- Write source code in `.uf90` using greek symbols
- Run `uf90-sync`
- `.uf90` files are translated into `.f90`
- Build the project normally with `fpm`

The generated `.f90` files are the files actually compiled.

---

What this tool does
-------------------

- Allows a small and explicit set of Unicode symbols
- Generates portable, standard Fortran code
- Integrates with `fpm` workflows
- Stops with an error if unsupported constructs are found

---

What this tool does not do
--------------------------

- Does not change Fortran semantics
- Does not add new language features
- Does not allow arbitrary Unicode
- Does not depend on a specific editor or IDE
- Does not hide the code that is compiled

Unsupported usage is rejected explicitly.

---

Prerequisites
-------------

- A Fortran compiler
- Fortran Package Manager (fpm)

---

Installation
------------

```bash
git clone https://github.com/nnardoto/uf90
cd uf90
fpm build
fpm install --prefix ~/.local/bin
```

Usage
-----
Example usage inside an existing fpm project, you may create a bash file like this
```bash
#!/bin/bash

# Translate .uf90 to .f90
uf90-sync

# Build the project
fpm build
```

Supported Symbols
-----------------

Only the symbols listed below are accepted in `.uf90` files.  
Each symbol is translated into a deterministic ASCII identifier in the generated `.f90` file.  
Any other Unicode symbol is rejected.

| Category        | _latex code_   | Symbol | Generated identifier |
|-----------------|----------------|--------|----------------------|
| Greek lowercase | `\alpha`       | α      | `alpha`              |
|                 | `\beta`        | β      | `beta`               |
|                 | `\gamma`       | γ      | `gamma`              |
|                 | `\delta`       | δ      | `delta`              |
|                 | `\epsilon`     | ε      | `epsilon`            |
|                 | `\zeta`        | ζ      | `zeta`               |
|                 | `\eta`         | η      | `eta`                |
|                 | `\theta`       | θ      | `theta`              |
|                 | `\iota`        | ι      | `iota`               |
|                 | `\kappa`       | κ      | `kappa`              |
|                 | `\lambda`      | λ      | `lambda`             |
|                 | `\mu`          | μ      | `mu`                 |
|                 | `\nu`          | ν      | `nu`                 |
|                 | `\xi`          | ξ      | `xi`                 |
|                 | `\omicron`     | ο      | `omicron`            |
|                 | `\pi`          | π      | `pi`                 |
|                 | `\rho`         | ρ      | `rho`                |
|                 | `\sigma`       | σ      | `sigma`              |
|                 | `\tau`         | τ      | `tau`                |
|                 | `\upsilon`     | υ      | `upsilon`            |
|                 | `\phi`         | φ      | `phi`                |
|                 | `\chi`         | χ      | `chi`                |
|                 | `\psi`         | ψ      | `psi`                |
|                 | `\omega`       | ω      | `omega`              |
| Greek uppercase | `\Alpha`       | Α      | `uc_alpha`           |
|                 | `\Beta`        | Β      | `uc_beta`            |
|                 | `\Gamma`       | Γ      | `uc_gamma`           |
|                 | `\Delta`       | Δ      | `uc_delta`           |
|                 | `\Epsilon`     | Ε      | `uc_epsilon`         |
|                 | `\Zeta`        | Ζ      | `uc_zeta`            |
|                 | `\Eta`         | Η      | `uc_eta`             |
|                 | `\Theta`       | Θ      | `uc_theta`           |
|                 | `\Iota`        | Ι      | `uc_iota`            |
|                 | `\Kappa`       | Κ      | `uc_kappa`           |
|                 | `\Lambda`      | Λ      | `uc_lambda`          |
|                 | `\Mu`          | Μ      | `uc_mu`              |
|                 | `\Nu`          | Ν      | `uc_nu`              |
|                 | `\Xi`          | Ξ      | `uc_xi`              |
|                 | `\Omicron`     | Ο      | `uc_omicron`         |
|                 | `\Pi`          | Π      | `uc_pi`              |
|                 | `\Rho`         | Ρ      | `uc_rho`             |
|                 | `\Sigma`       | Σ      | `uc_sigma`           |
|                 | `\Tau`         | Τ      | `uc_tau`             |
|                 | `\Upsilon`     | Υ      | `uc_upsilon`         |
|                 | `\Phi`         | Φ      | `uc_phi`             |
|                 | `\Chi`         | Χ      | `uc_chi`             |
|                 | `\Psi`         | Ψ      | `uc_psi`             |
|                 | `\Omega`       | Ω      | `uc_omega`           |



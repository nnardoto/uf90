# Symbol Reference

Complete reference of all Unicode symbols supported by uf90.

## Quick Reference

| Symbol | ASCII | LaTeX | Description |
|--------|-------|-------|-------------|
| α | `alpha` | `\alpha` | Alpha (lowercase) |
| β | `beta` | `\beta` | Beta (lowercase) |
| Δ | `uc_delta` | `\Delta` | Delta (uppercase) |
| π | `pi` | `\pi` | Pi |
| σ | `sigma` | `\sigma` | Sigma (lowercase) |
| Σ | `uc_sigma` | `\Sigma` | Sigma (uppercase) |
| ω | `omega` | `\omega` | Omega (lowercase) |
| Ω | `uc_omega` | `\Omega` | Omega (uppercase) |
| ₀ | `_0` | `_0` | Subscript 0 |
| ₁₂ | `_12` | `_{12}` | Subscript 12 (consecutive) |
| ² | `_p2` | `^2` | Superscript 2 |

## Greek Letters

### Lowercase Greek Alphabet

| Unicode | ASCII | LaTeX | Name | Common Use |
|---------|-------|-------|------|------------|
| α | `alpha` | `\alpha` | Alpha | Angles, coefficients |
| β | `beta` | `\beta` | Beta | Angles, decay rates |
| γ | `gamma` | `\gamma` | Gamma | Angles, Lorentz factor |
| δ | `delta` | `\delta` | Delta | Small change |
| ε | `epsilon` | `\epsilon` | Epsilon | Small quantity, permittivity |
| ζ | `zeta` | `\zeta` | Zeta | Damping ratio |
| η | `eta` | `\eta` | Eta | Efficiency |
| θ | `theta` | `\theta` | Theta | Angles |
| ι | `iota` | `\iota` | Iota | Rarely used |
| κ | `kappa` | `\kappa` | Kappa | Curvature |
| λ | `lambda` | `\lambda` | Lambda | Wavelength, eigenvalue |
| μ | `mu` | `\mu` | Mu | Mean, permeability |
| ν | `nu` | `\nu` | Nu | Frequency, kinematic viscosity |
| ξ | `xi` | `\xi` | Xi | Random variable |
| ο | `omicron` | `\omicron` | Omicron | Rarely used |
| π | `pi` | `\pi` | Pi | 3.14159... |
| ρ | `rho` | `\rho` | Rho | Density |
| σ | `sigma` | `\sigma` | Sigma | Standard deviation, stress |
| τ | `tau` | `\tau` | Tau | Time constant, shear stress |
| υ | `upsilon` | `\upsilon` | Upsilon | Rarely used |
| φ | `phi` | `\phi` | Phi | Angles, potential |
| χ | `chi` | `\chi` | Chi | Chi-squared distribution |
| ψ | `psi` | `\psi` | Psi | Wave function |
| ω | `omega` | `\omega` | Omega | Angular frequency |

### Uppercase Greek Alphabet

| Unicode | ASCII | LaTeX | Name | Common Use |
|---------|-------|-------|------|------------|
| Α | `uc_alpha` | `\Alpha` | Alpha | Capital alpha |
| Β | `uc_beta` | `\Beta` | Beta | Capital beta |
| Γ | `uc_gamma` | `\Gamma` | Gamma | Gamma function |
| Δ | `uc_delta` | `\Delta` | Delta | Change, finite difference |
| Ε | `uc_epsilon` | `\Epsilon` | Epsilon | Capital epsilon |
| Ζ | `uc_zeta` | `\Zeta` | Zeta | Capital zeta |
| Η | `uc_eta` | `\Eta` | Eta | Capital eta |
| Θ | `uc_theta` | `\Theta` | Theta | Angle (capital) |
| Ι | `uc_iota` | `\Iota` | Iota | Capital iota |
| Κ | `uc_kappa` | `\Kappa` | Kappa | Capital kappa |
| Λ | `uc_lambda` | `\Lambda` | Lambda | Cosmological constant |
| Μ | `uc_mu` | `\Mu` | Mu | Capital mu |
| Ν | `uc_nu` | `\Nu` | Nu | Capital nu |
| Ξ | `uc_xi` | `\Xi` | Xi | Capital xi |
| Ο | `uc_omicron` | `\Omicron` | Omicron | Capital omicron |
| Π | `uc_pi` | `\Pi` | Pi | Product operator |
| Ρ | `uc_rho` | `\Rho` | Rho | Capital rho |
| Σ | `uc_sigma` | `\Sigma` | Sigma | Summation operator |
| Τ | `uc_tau` | `\Tau` | Tau | Capital tau |
| Υ | `uc_upsilon` | `\Upsilon` | Upsilon | Capital upsilon |
| Φ | `uc_phi` | `\Phi` | Phi | Potential (capital) |
| Χ | `uc_chi` | `\Chi` | Chi | Capital chi |
| Ψ | `uc_psi` | `\Psi` | Psi | Wave function (capital) |
| Ω | `uc_omega` | `\Omega` | Omega | Ohms, solid angle |

### Special Note: Delta

There are TWO Unicode codepoints for Delta:
- `Δ` (U+0394) - Greek capital letter Delta
- `∆` (U+2206) - Increment operator Delta

Both translate to `uc_delta` in uf90.

## Subscripts and Superscripts

### Numeric Subscripts

| Unicode | ASCII | LaTeX | Example |
|---------|-------|-------|---------|
| ₀ | `_0` | `_0` | `x₀` → `x_0` |
| ₁ | `_1` | `_1` | `x₁` → `x_1` |
| ₂ | `_2` | `_2` | `x₂` → `x_2` |
| ₃ | `_3` | `_3` | `x₃` → `x_3` |
| ₄ | `_4` | `_4` | `x₄` → `x_4` |
| ₅ | `_5` | `_5` | `x₅` → `x_5` |
| ₆ | `_6` | `_6` | `x₆` → `x_6` |
| ₇ | `_7` | `_7` | `x₇` → `x_7` |
| ₈ | `_8` | `_8` | `x₈` → `x_8` |
| ₉ | `_9` | `_9` | `x₉` → `x_9` |

**Consecutive subscripts** are merged:
- `U₁₂` → `U_12` (not `U_1_2`)
- `T₁₀₀` → `T_100` (not `T_1_0_0`)

### Numeric Superscripts

| Unicode | ASCII | LaTeX | Example |
|---------|-------|-------|---------|
| ⁰ | `_p0` | `^0` | `x⁰` → `x_p0` |
| ¹ | `_p1` | `^1` | `x¹` → `x_p1` |
| ² | `_p2` | `^2` | `x²` → `x_p2` |
| ³ | `_p3` | `^3` | `x³` → `x_p3` |
| ⁴ | `_p4` | `^4` | `x⁴` → `x_p4` |
| ⁵ | `_p5` | `^5` | `x⁵` → `x_p5` |
| ⁶ | `_p6` | `^6` | `x⁶` → `x_p6` |
| ⁷ | `_p7` | `^7` | `x⁷` → `x_p7` |
| ⁸ | `_p8` | `^8` | `x⁸` → `x_p8` |
| ⁹ | `_p9` | `^9` | `x⁹` → `x_p9` |

Note: `_p` prefix means "power"/"superscript"

## Usage Examples

### Physics

```fortran
! Kinematics
real :: v₀, v₁, Δt
real :: a, Δv

Δv = v₁ - v₀
a = Δv / Δt

! Energy
real :: E, m, c²
c² = (3.0e8)**2
E = m * c²

! Waves
real :: λ, ν, c
ν = c / λ

! Electromagnetic
real :: ε₀, μ₀
real :: E, B
```

### Statistics

```fortran
! Moments
real :: μ, σ², σ
real :: skewness, kurtosis

μ = mean(data)
σ² = variance(data)
σ = sqrt(σ²)

! Distributions
real :: Φ  ! CDF of normal
real :: χ²  ! Chi-squared statistic
```

### Mathematics

```fortran
! Summation
real :: Σ, Π
Σ = sum(array)
Π = product(array)

! Angles
real :: α, β, γ, θ, φ
real :: sin_α, cos_β

! Complex
real :: ρ, θ
complex :: z
z = ρ * exp((0,1) * θ)
```

### Engineering

```fortran
! Stress-strain
real :: σ_x, σ_y, τ_xy
real :: ε_x, ε_y, γ_xy

! Fluid dynamics
real :: ρ, μ, ν
ν = μ / ρ  ! Kinematic viscosity

! Heat transfer
real :: α_thermal
real :: λ_conductivity
```

## Input Methods

### Linux

**Using Unicode input:**
```
Ctrl+Shift+U, then hex code, then Enter
α: Ctrl+Shift+U 03B1 Enter
β: Ctrl+Shift+U 03B2 Enter
```

**Using compose key:**
```
Configure compose key in system settings
Then: Compose * a → α
      Compose * b → β
```

### macOS

**Character Viewer:**
```
Ctrl+Cmd+Space
Search for "alpha", "beta", etc.
```

**Greek keyboard:**
```
Enable Greek keyboard in System Preferences
Switch with Cmd+Space
Type normally: a → α, b → β
```

### Windows

**Alt codes:**
```
α: Alt+224
β: Alt+225
(Limited set available)
```

**Character Map:**
```
Win+R → charmap
Find and copy symbols
```

### Editors

**VS Code:**
- Install "Unicode Math Input" extension
- Type `\alpha` → α (with snippet)

**Vim:**
- In insert mode: `Ctrl+K a*` → α
- Or: `Ctrl+K b*` → β

**Emacs:**
```elisp
;; Add to init.el
(set-input-method "TeX")
;; Then: \alpha → α
```

## Reserved Identifiers

These ASCII names CANNOT be used in .f90u files:

**Lowercase Greek:**
`alpha`, `beta`, `gamma`, `delta`, `epsilon`, `zeta`, `eta`, `theta`, `iota`, `kappa`, `lambda`, `mu`, `nu`, `xi`, `omicron`, `pi`, `rho`, `sigma`, `tau`, `upsilon`, `phi`, `chi`, `psi`, `omega`

**Uppercase Greek (with prefix):**
`uc_alpha`, `uc_beta`, `uc_gamma`, `uc_delta`, `uc_epsilon`, `uc_zeta`, `uc_eta`, `uc_theta`, `uc_iota`, `uc_kappa`, `uc_lambda`, `uc_mu`, `uc_nu`, `uc_xi`, `uc_omicron`, `uc_pi`, `uc_rho`, `uc_sigma`, `uc_tau`, `uc_upsilon`, `uc_phi`, `uc_chi`, `uc_psi`, `uc_omega`

**Why?** To avoid ambiguity. Use the Unicode symbols instead!

```fortran
! ✗ WRONG (will cause error)
real :: alpha, beta

! ✓ CORRECT
real :: α, β
```

## Symbol Categories

### Commonly Used (recommended)

| Symbol | ASCII | Use |
|--------|-------|-----|
| α, β, γ | `alpha`, `beta`, `gamma` | Angles, coefficients |
| δ, Δ | `delta`, `uc_delta` | Small/large changes |
| ε | `epsilon` | Small quantities |
| θ, φ | `theta`, `phi` | Angles |
| λ | `lambda` | Wavelength, eigenvalues |
| μ, σ | `mu`, `sigma` | Mean, std deviation |
| π | `pi` | 3.14159... |
| ρ | `rho` | Density |
| τ | `tau` | Time constants |
| ω, Ω | `omega`, `uc_omega` | Angular freq, ohms |

### Occasionally Used

| Symbol | ASCII | Use |
|--------|-------|-----|
| ζ | `zeta` | Damping ratio |
| η | `eta` | Efficiency |
| κ | `kappa` | Curvature |
| ν | `nu` | Frequency, viscosity |
| ξ | `xi` | Random variables |
| χ | `chi` | Chi-squared |
| ψ, Ψ | `psi`, `uc_psi` | Wave functions |
| Γ | `uc_gamma` | Gamma function |
| Λ | `uc_lambda` | Cosmological constant |
| Σ | `uc_sigma` | Summation |
| Π | `uc_pi` | Product |
| Φ | `uc_phi` | Potential |

### Rarely Used

All other Greek letters. Supported but uncommon in typical code.

## Tips for Choosing Symbols

1. **Match paper notation** - Use same symbols as in papers/books
2. **Be consistent** - Don't mix ASCII and Unicode for same concept
3. **Add comments** - Explain what each symbol represents
4. **Consider readability** - Some symbols may be hard to distinguish
5. **Use prefixes** - Add descriptive prefixes when needed (`T_max`, not just `T`)

## Example: Well-Documented Physics Code

```fortran
module wave_propagation
  implicit none
  
  ! Physical constants
  real, parameter :: c = 299792458.0_8  ! Speed of light [m/s]
  real, parameter :: ε₀ = 8.854e-12_8   ! Vacuum permittivity [F/m]
  real, parameter :: μ₀ = 1.257e-6_8    ! Vacuum permeability [H/m]
  
contains
  
  subroutine wave_parameters(λ, ν, ω, k)
    !> Calculate wave parameters
    !! @param λ  Wavelength [m]
    !! @param ν  Frequency [Hz]
    !! @param ω  Angular frequency [rad/s]
    !! @param k  Wave number [1/m]
    
    real, intent(in) :: λ
    real, intent(out) :: ν, ω, k
    
    real, parameter :: π = 3.14159265358979_8
    
    ν = c / λ        ! Frequency
    ω = 2.0 * π * ν  ! Angular frequency
    k = 2.0 * π / λ  ! Wave number
    
  end subroutine wave_parameters
  
end module wave_propagation
```

---

**See also:**
- [USAGE.md](USAGE.md) - How to use these symbols
- [examples/](../examples/) - More examples
- [Unicode Math Symbols](https://en.wikipedia.org/wiki/Mathematical_operators_and_symbols_in_Unicode) - Full Unicode reference

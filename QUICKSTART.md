# Quick Start Guide

Get up and running with uf90 in under 5 minutes!

## Choose Your Path

### 🐍 Python (Easiest - No Compilation)

```bash
# 1. Download
cd uf90/python
chmod +x unicode_fortran_refactored.py

# 2. Use immediately
./unicode_fortran_refactored.py --help

# 3. Translate your first file
./unicode_fortran_refactored.py ../examples/exemplo.uf90
```

**Done!** Your translated file is ready.

---

### 🚀 Fortran (Best for FPM Projects)

```bash
# 1. Ensure you have FPM and a Fortran compiler
fpm --version
gfortran --version

# 2. Build uf90-sync
fpm build

# 3. Install
fpm install --prefix ~/.local

# 4. Add to PATH (add this to ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"

# 5. Use in any FPM project
cd your-fpm-project/
uf90-sync
```

**Done!** All your `.uf90` files are now synced.

---

## Your First Unicode Fortran File

Create `hello_unicode.uf90`:

```fortran
program hello_unicode
  implicit none
  
  ! Greek letters for variables
  real :: α, β, π
  real :: result
  
  ! Initialize
  π = 3.14159
  α = 2.0
  β = 3.0
  
  ! Calculate
  result = α * β * π
  
  ! Output
  print *, "α =", α
  print *, "β =", β
  print *, "π =", π
  print *, "Result =", result
  
end program hello_unicode
```

Translate it:

```bash
# Python
./python/unicode_fortran_refactored.py hello_unicode.uf90

# Fortran (in FPM project)
uf90-sync
```

Compile and run:

```bash
gfortran hello_unicode.f90 -o hello
./hello
```

---

## Common Workflows

### Workflow 1: Standalone File

```bash
# Create .uf90 file
vim physics.uf90

# Translate (Python)
uf90-py physics.uf90

# Compile
gfortran physics.f90 -o physics

# Run
./physics
```

### Workflow 2: FPM Project

```bash
# Initialize project
fpm init my_project
cd my_project

# Create .uf90 files in src/
vim src/my_module.uf90

# Sync
uf90-sync

# Build (automatically uses .f90 files)
fpm build

# Run
fpm run
```

### Workflow 3: Existing Project

```bash
# In your existing project
cd existing_project/

# Create .uf90 versions of your files
cp src/module.f90 src/module.uf90
vim src/module.uf90  # Add Unicode symbols

# Sync
uf90-sync

# Verify
diff src/module.f90 <original>  # Should show Unicode → ASCII

# Build as normal
make  # or fpm build
```

---

## Essential Commands

### Python Version

```bash
# Basic
uf90-py file.uf90                    # Creates file.f90

# With options
uf90-py file.uf90 -o custom.f90      # Custom output
uf90-py -v file.uf90                 # Verbose
uf90-py --generate-table             # Create reference

# Get help
uf90-py --help
```

### Fortran Version

```bash
# In any FPM project
uf90-sync                            # Sync all .uf90 files

# That's it! No options needed
# (Automatically finds and processes all files)
```

---

## Frequently Used Symbols

Copy-paste these into your code:

```fortran
! Greek lowercase
α β γ δ ε ζ η θ κ λ μ ν π ρ σ τ φ χ ψ ω

! Greek uppercase  
Γ Δ Θ Λ Ξ Π Σ Φ Ψ Ω

! Subscripts
₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉

! Superscripts
⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹
```

**How to type these?**
- Linux: Ctrl+Shift+U then code (e.g., `03B1` for α)
- macOS: Ctrl+Cmd+Space (Character Viewer)
- Windows: Character Map or Alt codes
- Editors: See [docs/SYMBOLS.md](docs/SYMBOLS.md)

---

## Quick Examples

### Physics

```fortran
real :: λ, ν, c
c = 3.0e8
λ = 500.0e-9  ! 500 nm
ν = c / λ     ! Frequency
```

### Statistics

```fortran
real :: μ, σ², data(100)
μ = sum(data) / 100.0
σ² = sum((data - μ)**2) / 100.0
```

### Mathematics

```fortran
real :: α, β, γ
α = 30.0 * π / 180.0  ! Convert to radians
β = sin(α)
γ = cos(α)
```

---

## Next Steps

1. **Read the full docs**: [docs/USAGE.md](docs/USAGE.md)
2. **See all symbols**: [docs/SYMBOLS.md](docs/SYMBOLS.md)
3. **Try examples**: [examples/](examples/)
4. **Configure your editor**: See [docs/USAGE.md#input-methods](docs/USAGE.md#input-methods)

---

## Troubleshooting

**Q: "command not found"**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
# Add this line to ~/.bashrc for persistence
```

**Q: "Permission denied"**
```bash
chmod +x unicode_fortran_refactored.py
# or
chmod +x ~/.local/bin/uf90-sync
```

**Q: "Python version too old"**
```bash
python3 --version  # Need 3.6+
# Update Python via your package manager
```

**Q: "FPM not found"**
```bash
# Install FPM: https://fpm.fortran-lang.org/install/
```

---

## Getting Help

- 📖 [Full Documentation](docs/USAGE.md)
- 💬 [GitHub Discussions](https://github.com/seu-usuario/uf90/discussions)
- 🐛 [Report Issues](https://github.com/seu-usuario/uf90/issues)

---

**Happy coding with Unicode Fortran!** ✨

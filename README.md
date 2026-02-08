# uf90 - Unicode Fortran Translator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FPM](https://img.shields.io/badge/FPM-package-blueviolet)](https://fpm.fortran-lang.org)
[![Fortran](https://img.shields.io/badge/Fortran-2008+-blue.svg)](https://fortran-lang.org)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org)

Write beautiful, readable Fortran code using Unicode symbols (Greek letters, subscripts, etc.) that gets automatically translated to standard ASCII before compilation.

```fortran
! Write this in your .uf90 file:
program physics
  real :: α, β, Δt
  real :: E, m, c²
  
  α = 0.1
  β = 0.2
  Δt = 1.0e-6
  
  c² = 299792458.0**2
  E = m * c²
end program physics
```

```fortran
! Automatically generates this standard .f90:
program physics
  real :: alpha, beta, uc_delta_t
  real :: E, m, c_p2
  
  alpha = 0.1
  beta = 0.2
  uc_delta_t = 1.0e-6
  
  c_p2 = 299792458.0**2
  E = m * c_p2
end program physics
```

## ✨ Features

- 🔤 **Full Greek alphabet support** (lowercase and uppercase)
- 🔢 **Subscripts and superscripts** (₀₁₂...₉, ⁰¹²...⁹)
- 📝 **Unicode preserved in comments** (optional)
- 🔒 **Safe overwrites** (won't overwrite manual .f90 files)
- ⚡ **Incremental sync** (only translates modified files)
- 🐍 **Two implementations**: Native Fortran (fast) or Python (portable)
- 📦 **FPM integration** (seamless workflow)
- 🧪 **Well tested** with comprehensive examples

## 🚀 Quick Start

### Using Fortran (Recommended for FPM projects)

```bash
# Install from FPM registry (coming soon)
fpm install uf90

# Or build from source
git clone https://github.com/seu-usuario/uf90.git
cd uf90
fpm install --prefix ~/.local

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

**Usage in your FPM project:**

```bash
# 1. Create .uf90 files in src/, app/, or test/
vim src/my_module.uf90

# 2. Sync (generates .f90 files)
uf90-sync

# 3. Build normally
fpm build
```

### Using Python (Standalone, no FPM needed)

```bash
# Download
wget https://raw.githubusercontent.com/seu-usuario/uf90/main/python/unicode_fortran_refactored.py
chmod +x unicode_fortran_refactored.py

# Translate a file
./unicode_fortran_refactored.py my_code.uf90

# Or install globally
sudo cp unicode_fortran_refactored.py /usr/local/bin/uf90-py
sudo chmod +x /usr/local/bin/uf90-py
```

## 📖 Documentation

### Supported Symbols

| Category | Examples | ASCII Output |
|----------|----------|--------------|
| **Greek lowercase** | α β γ δ ... ω | `alpha` `beta` `gamma` `delta` ... `omega` |
| **Greek uppercase** | Α Β Γ Δ ... Ω | `uc_alpha` `uc_beta` `uc_gamma` `uc_delta` ... `uc_omega` |
| **Subscripts** | x₀ x₁ x₂ ... x₉ | `x_0` `x_1` `x_2` ... `x_9` |
| **Superscripts** | x⁰ x¹ x² ... x⁹ | `x_p0` `x_p1` `x_p2` ... `x_p9` |
| **Consecutive subscripts** | U₁₂ T₁₀₀ | `U_12` `T_100` (not `U_1_2`!) |

**Note**: Unicode in comments is preserved by default.

See [docs/SYMBOLS.md](docs/SYMBOLS.md) for the complete list.

### Advanced Usage

**Fortran (uf90-sync):**
- Automatically finds all `.uf90` files in `src/`, `app/`, `test/`
- Only regenerates files that changed (efficient)
- Protects manually-created `.f90` files from overwriting
- Run inside any FPM project directory

**Python (unicode_fortran_refactored.py):**
```bash
# Basic usage
python3 unicode_fortran_refactored.py input.uf90

# Specify output
python3 unicode_fortran_refactored.py input.uf90 -o output.f90

# Translate Unicode in comments too
python3 unicode_fortran_refactored.py input.uf90 --no-preserve

# Verbose mode
python3 unicode_fortran_refactored.py -v input.uf90

# Generate reference table
python3 unicode_fortran_refactored.py --generate-table
```

See [docs/USAGE.md](docs/USAGE.md) for detailed examples.

## 🔧 Integration Examples

### Makefile Integration

```makefile
.PHONY: sync build clean

sync:
	uf90-sync

build: sync
	fpm build

clean:
	rm -rf build/
	find . -name '*.f90' -path '*/src/*' -o -path '*/app/*' -o -path '*/test/*' | \
		head -n1 | xargs grep -l "GENERATED FROM .uf90" | xargs rm -f

run: build
	fpm run
```

### Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
# Auto-sync .uf90 files before commit

if command -v uf90-sync &> /dev/null; then
    uf90-sync
    git add -u '*.f90'
fi
```

### CI/CD (GitHub Actions)

See [.github/workflows/ci.yml](.github/workflows/ci.yml) for complete example.

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: fortran-lang/setup-fpm@v5
      - name: Build uf90-sync
        run: fpm build
      - name: Install uf90-sync
        run: fpm install --prefix ~/.local
      - name: Sync Unicode files
        run: ~/.local/bin/uf90-sync
      - name: Build project
        run: fpm build
```

## 🎯 Why uf90?

### Before (ASCII Fortran):
```fortran
real :: alpha_1, alpha_2, beta_max
real :: delta_x, delta_y, delta_t
real :: sigma_squared, mu_mean
real :: lambda_wavelength

! Code is verbose and less readable
! Greek letters spelled out lose their mathematical meaning
! Subscripts are clumsy with underscores
```

### After (Unicode Fortran):
```fortran
real :: α₁, α₂, β_max
real :: Δx, Δy, Δt
real :: σ², μ_mean
real :: λ_wavelength

! Code is concise and mathematically intuitive
! Matches equations in papers directly
! Natural subscript notation
```

**Benefits:**
- ✅ Write code that looks like the mathematics
- ✅ Easier to translate papers → code
- ✅ More readable, especially for physics/engineering
- ✅ Still compiles to standard Fortran
- ✅ No runtime overhead (translation happens before compilation)

## 🏗️ Project Structure

```
uf90/
├── src/                    # Fortran source modules
│   ├── uf90_constants.f90           # Global constants
│   ├── uf90_translation_rules.f90   # Unicode→ASCII mappings
│   └── uf90_file_translator.f90     # File I/O and translation logic
├── app/                    # Executable programs
│   └── uf90_sync_main.f90           # Main uf90-sync program
├── python/                 # Python implementation
│   └── unicode_fortran_refactored.py  # Standalone translator
├── test/                   # Unit tests (coming soon)
├── docs/                   # Additional documentation
│   ├── USAGE.md                     # Detailed usage guide
│   ├── SYMBOLS.md                   # Complete symbol reference
│   ├── ARCHITECTURE.md              # Design decisions
│   └── COMPARISON.md                # Python vs Fortran comparison
├── examples/               # Example projects
│   ├── basic/                       # Simple examples
│   ├── physics/                     # Physics simulations
│   └── math/                        # Mathematical computing
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD configuration
├── fpm.toml               # FPM package manifest
├── LICENSE                # MIT License
└── README.md              # This file
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

**Areas we'd love help with:**
- 🧪 More comprehensive test suite
- 📝 Additional documentation and examples
- 🌍 Support for more Unicode symbols
- 🔧 Editor integrations (VS Code, Vim, Emacs)
- 📦 Package management (Spack, Conda, etc.)
- 🐛 Bug reports and fixes

## 📊 Comparison: Python vs Fortran

| Feature | Python | Fortran |
|---------|--------|---------|
| **Installation** | ⭐⭐⭐⭐⭐ Just download | ⭐⭐⭐ Need FPM + compiler |
| **Speed** | ⭐⭐⭐ Fast enough | ⭐⭐⭐⭐⭐ Very fast |
| **FPM Integration** | ⭐⭐ External script | ⭐⭐⭐⭐⭐ Native |
| **Portability** | ⭐⭐⭐⭐⭐ Runs anywhere | ⭐⭐⭐⭐ After compilation |
| **Easy to modify** | ⭐⭐⭐⭐⭐ Very easy | ⭐⭐⭐ Moderate |

**Recommendation:**
- Use **Python** for quick one-off translations or if you don't have FPM
- Use **Fortran** for FPM projects and production workflows

See [docs/COMPARISON.md](docs/COMPARISON.md) for detailed analysis.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

You are free to use this software for any purpose, including commercial applications.

## 🙏 Acknowledgments

- Fortran community for feedback and suggestions
- FPM team for the excellent build system
- Unicode Consortium for standardizing mathematical symbols

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/uf90/issues)
- **Discussions**: [GitHub Discussions](https://github.com/seu-usuario/uf90/discussions)
- **Email**: community@uf90.dev

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ for the Fortran community**

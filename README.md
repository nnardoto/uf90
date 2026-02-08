# uf90 - Unicode Fortran Translator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FPM](https://img.shields.io/badge/FPM-package-blueviolet)](https://fpm.fortran-lang.org)
[![Fortran](https://img.shields.io/badge/Fortran-2008+-blue.svg)](https://fortran-lang.org)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org)

Write beautiful, readable Fortran code using Unicode symbols (Greek letters, subscripts, etc.) that gets automatically translated to standard ASCII before compilation.

**New in 2.0:** Now uses `.f90u` extension (more universal) and includes `fpm-unicode` wrapper for automatic translation!

```fortran
! Write this in your .f90u file:
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

- 🔤 **Full Greek alphabet** support (lowercase and uppercase)
- 🔢 **Subscripts and superscripts** (₀₁₂...₉, ⁰¹²...⁹)
- 📝 **Comments preserved** (Unicode stays in comments by default)
- 🔒 **Safe overwrites** (won't destroy manual .f90 files)
- ⚡ **Incremental sync** (only translates changed files)
- 🎯 **`.f90u` extension** (universal, follows naming conventions)
- 🚀 **`fpm-unicode` wrapper** (automatic translation before build!)
- 🐍 **Two implementations**: Fortran (fast) or Python (portable)
- 📦 **FPM integrated** (seamless workflow)

## 🚀 Quick Start

### Option 1: Integrated Workflow (Recommended)

```bash
# 1. Install uf90 toolkit
git clone https://github.com/seu-usuario/uf90.git
cd uf90
fpm install --prefix ~/.local
export PATH="$HOME/.local/bin:$PATH"

# 2. In your FPM project, create .f90u files
cat > src/my_module.f90u << 'EOF'
module my_module
  real :: π = 3.14159
  real :: α, β
end module
EOF

# 3. Use fpm-unicode instead of fpm (auto-translates!)
fpm-unicode build
fpm-unicode run
fpm-unicode test
```

### Option 2: Manual Workflow

```bash
# 1. Install uf90-sync only
fpm install --prefix ~/.local

# 2. In your project, sync manually
uf90-sync          # Translates all .f90u → .f90

# 3. Build normally
fpm build
```

### Option 3: Python Standalone

```bash
# 1. Download Python script
cd uf90/python
chmod +x unicode_fortran_refactored.py

# 2. Translate files
./unicode_fortran_refactored.py my_code.f90u

# 3. Compile normally
gfortran my_code.f90 -o my_program
```

## 📖 Understanding `.f90u` Extension

### Why `.f90u`?

- **Universal naming**: Base name + `u` suffix (common pattern)
- **Clear meaning**: "Fortran 90 Unicode"
- **Editor friendly**: Easy to configure syntax highlighting
- **Community standard**: Follows conventions from other languages

### Comparison

| Extension | Meaning | Status |
|-----------|---------|--------|
| `.f90u` | Fortran 90 Unicode | ✅ **Recommended** (v2.0+) |
| `.f90u` | Unicode Fortran 90 | ⚠️ Legacy (v1.x) |

Both work, but `.f90u` is preferred going forward.

## 🔧 The `fpm-unicode` Wrapper

The `fpm-unicode` command is a smart wrapper that:

1. **Automatically syncs** `.f90u` files before any FPM command
2. **Works transparently** - just replace `fpm` with `fpm-unicode`
3. **Shows progress** - colored output with status messages
4. **Handles errors** - stops if translation fails

### Usage

```bash
# Instead of:          # Use:
fpm build             fpm-unicode build
fpm run               fpm-unicode run  
fpm test              fpm-unicode test
fpm install           fpm-unicode install

# Any FPM command works!
fpm-unicode build --profile release
fpm-unicode run --example my_example
```

### What Happens Behind the Scenes

```
fpm-unicode build
    ↓
1. Checks for fpm.toml ✓
2. Finds uf90-sync ✓
3. Runs: uf90-sync
   → Translates .f90u → .f90
4. Runs: fpm build
   → Compiles .f90 files
5. Shows summary ✓
```

## 📚 Workflows

### Workflow 1: Fully Automated (Best for most projects)

```bash
# Setup (once)
fpm install --prefix ~/.local

# Daily use (in your project)
vim src/physics.f90u              # Edit Unicode source
fpm-unicode build                 # Auto-translates + compiles
fpm-unicode run                   # Auto-translates + runs
```

**Advantages:**
- ✅ Never forget to sync
- ✅ One command does everything
- ✅ Perfect for teams

### Workflow 2: Makefile Integration

Create a `Makefile` (see `examples/Makefile`):

```makefile
build:
	uf90-sync
	fpm build

run: build
	fpm run

clean:
	rm -rf build/
	find . -name "*.f90" -path "*src/*" | \
		xargs grep -l "GENERATED FROM .f90u" | \
		xargs rm -f
```

Then just use `make`:
```bash
make build
make run
make clean
```

### Workflow 3: Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
uf90-sync
git add -u '*.f90'
```

Auto-syncs before every commit!

### Workflow 4: Manual Control

```bash
# When you want explicit control
vim src/module.f90u
uf90-sync                         # Explicit sync
git diff src/module.f90           # Review changes
fpm build                         # Standard build
```

## 📋 Symbol Reference

### Greek Letters

| Unicode | ASCII | Example |
|---------|-------|---------|
| α β γ δ | `alpha` `beta` `gamma` `delta` | `real :: α` |
| Δ Σ Ω | `uc_delta` `uc_sigma` `uc_omega` | `real :: Δt` |

### Subscripts & Superscripts

| Unicode | ASCII | Example |
|---------|-------|---------|
| x₀ x₁ x₂ | `x_0` `x_1` `x_2` | `real :: v₀` |
| x² x³ | `x_p2` `x_p3` | `E = m * c²` |
| T₁₀₀ | `T_100` (merged!) | `real :: T₁₀₀` |

See [docs/SYMBOLS.md](docs/SYMBOLS.md) for complete reference.

## 🏗️ Project Structure

```
uf90/
├── src/                    # Fortran modules
│   ├── uf90_constants.f90
│   ├── uf90_translation_rules.f90
│   └── uf90_file_translator.f90
├── app/                    # Executables
│   └── uf90_sync_main.f90
├── python/                 # Python version
│   └── unicode_fortran_refactored.py
├── fpm-unicode             # FPM wrapper script
├── fpm.toml               # FPM configuration
├── docs/                   # Documentation
│   ├── USAGE.md
│   └── SYMBOLS.md
└── examples/
    ├── Makefile           # Example Makefile
    ├── exemplo.f90u       # Example code
    └── exemplo.f90        # Translated output
```

## 🎯 Migration from v1.x

If you were using `.f90u` extension:

### Option 1: Rename Files (Recommended)

```bash
# Rename all .f90u → .f90u
find . -name "*.f90u" -exec sh -c '
  mv "$1" "${1%.f90u}.f90u"
' _ {} \;

# Update .gitignore
sed -i 's/\.f90u/.f90u/g' .gitignore
```

### Option 2: Keep Using `.f90u`

Both extensions work! The translator detects both:
- `file.f90u` → `file.f90` ✓
- `file.f90u` → `file.f90` ✓

But we recommend switching to `.f90u` for consistency.

## 🔍 How It Works

### Translation Process

```
1. Source file: physics.f90u
   ↓
2. uf90-sync reads and parses
   ↓
3. Validates identifiers (no reserved names)
   ↓
4. Translates Unicode → ASCII
   α → alpha
   β → beta
   Δt → uc_delta_t
   ↓
5. Writes: physics.f90
   (with generation marker)
   ↓
6. FPM compiles physics.f90
```

### Smart Features

- **Incremental**: Only translates modified files
- **Protected**: Won't overwrite manual `.f90` files
- **Reversible**: Keep both `.f90u` (source) and `.f90` (generated)
- **Git-friendly**: Commit both versions for safety

## 📦 Installation Details

### From Source

```bash
git clone https://github.com/seu-usuario/uf90.git
cd uf90
fpm build
fpm install --prefix ~/.local

# Add to PATH (add to ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
```

### Verify Installation

```bash
which uf90-sync        # Should show: ~/.local/bin/uf90-sync
which fpm-unicode      # Should show: ~/.local/bin/fpm-unicode

uf90-sync --help       # (no --help yet, just runs)
fpm-unicode build      # Should work in FPM project
```

### Files Installed

- `~/.local/bin/uf90-sync` - Translation tool
- `~/.local/bin/fpm-unicode` - FPM wrapper

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to add new Unicode symbols
- Code style guidelines
- Testing requirements
- Pull request process

## 📊 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Sync 10 files | ~0.1s | Only changed files |
| Sync 100 files | ~0.5s | Incremental |
| Full project (500 files) | ~2s | First time only |

The Fortran version is significantly faster than Python for large projects.

## 🐛 Troubleshooting

### "uf90-sync: command not found"
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc for persistence
```

### "fpm-unicode: uf90-sync not found"
```bash
# Reinstall
cd uf90
fpm install --prefix ~/.local
```

### "ERRO: identificador ASCII reservado"
You used `alpha`, `beta`, etc. directly in `.f90u` file.
Use Unicode: α, β instead.

### Reserved Names
Cannot use in `.f90u` files:
- `alpha`, `beta`, ..., `omega`
- `uc_alpha`, `uc_beta`, ..., `uc_omega`

Use the actual Unicode symbols instead!

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

Free for commercial and academic use.

## 🙏 Acknowledgments

- Fortran community for feedback
- FPM team for the excellent build system
- Contributors who suggested the `.f90u` naming convention

## 📬 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/uf90/issues)
- **Discussions**: [GitHub Discussions](https://github.com/seu-usuario/uf90/discussions)
- **Email**: community@uf90.dev

## ⭐ Quick Links

- 📖 [Usage Guide](docs/USAGE.md) - Detailed documentation
- 🔤 [Symbol Reference](docs/SYMBOLS.md) - All supported symbols
- 🤝 [Contributing](CONTRIBUTING.md) - How to contribute
- 🚀 [Quick Start](QUICKSTART.md) - 5-minute tutorial
- 🐍 [Python Version](python/README.md) - Standalone Python tool

---

**Made with ❤️ for the Fortran community**

*Now with `.f90u` extension and automatic `fpm-unicode` workflow!*

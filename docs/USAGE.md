# Usage Guide

Complete guide for using uf90 in your projects.

## Table of Contents

- [Quick Start](#quick-start)
- [Fortran Version](#fortran-version)
- [Python Version](#python-version)
- [Integration](#integration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 5-Minute Tutorial

```bash
# 1. Install (choose one)
fpm install uf90                    # Fortran version
# or
pip install uf90                    # Python version (coming soon)

# 2. Create a .uf90 file
cat > hello.uf90 << 'EOF'
program hello
  real :: α = 3.14
  print *, "α =", α
end program
EOF

# 3. Translate
uf90-sync                           # Fortran
# or
uf90-py hello.uf90                  # Python

# 4. Compile and run
fpm run                             # If using FPM
# or
gfortran hello.f90 -o hello && ./hello
```

## Fortran Version

### Installation

**From FPM registry:**
```bash
fpm install uf90
```

**From source:**
```bash
git clone https://github.com/seu-usuario/uf90.git
cd uf90
fpm build
fpm install --prefix ~/.local
export PATH="$HOME/.local/bin:$PATH"
```

### Usage in FPM Projects

**Project structure:**
```
my_project/
├── fpm.toml
├── src/
│   ├── module1.uf90
│   └── module2.uf90
├── app/
│   └── main.uf90
└── test/
    └── test_module1.uf90
```

**Workflow:**
```bash
# Edit .uf90 files
vim src/module1.uf90

# Sync (generates .f90)
uf90-sync

# Build normally
fpm build

# Run
fpm run
```

**What uf90-sync does:**
1. Searches `src/`, `app/`, `test/` for `.uf90` files
2. For each `.uf90`:
   - Checks if corresponding `.f90` needs regeneration
   - Validates no reserved identifiers used
   - Translates Unicode → ASCII
   - Writes `.f90` with generation marker
3. Skips files that haven't changed (fast!)
4. Refuses to overwrite manual `.f90` files

### Advanced Options

uf90-sync has no command-line options (simplicity by design).
It always:
- Runs from FPM project root
- Processes all `.uf90` files
- Preserves Unicode in comments
- Uses incremental updates

**To force regeneration:**
```bash
# Touch all .uf90 files
find . -name "*.uf90" -exec touch {} +
uf90-sync
```

**To clean generated files:**
```bash
# Find and remove generated .f90 files
find . -name "*.f90" -exec grep -l "GENERATED FROM .uf90" {} \; | xargs rm
```

## Python Version

### Installation

**Direct download:**
```bash
wget https://raw.githubusercontent.com/seu-usuario/uf90/main/python/unicode_fortran_refactored.py
chmod +x unicode_fortran_refactored.py
```

**Install globally:**
```bash
sudo cp unicode_fortran_refactored.py /usr/local/bin/uf90-py
sudo chmod +x /usr/local/bin/uf90-py
```

### Command-Line Usage

```bash
# Basic translation
uf90-py input.uf90

# Specify output file
uf90-py input.uf90 -o output.f90

# Translate Unicode in comments too
uf90-py input.uf90 --no-preserve

# Verbose mode (shows statistics)
uf90-py -v input.uf90

# Generate reference table
uf90-py --generate-table

# Help
uf90-py --help
```

### Python API

```python
from unicode_fortran_refactored import (
    UnicodeTranslator,
    FileProcessor,
    MappingRegistry
)

# Translate string
translator = UnicodeTranslator(preserve_comments=True)
result = translator.translate("real :: α, β")
print(result)  # "real :: alpha, beta"

# Process file
processor = FileProcessor(translator, verbose=True)
output_path = processor.process_file("input.uf90", "output.f90")

# Access mappings
registry = MappingRegistry()
mapping = registry.get_mapping('α')
print(mapping.ascii_replacement)  # "alpha"
```

## Integration

### Makefile Integration

```makefile
# Simple integration
.PHONY: all sync build clean

all: build

sync:
	@echo "Syncing .uf90 files..."
	@uf90-sync

build: sync
	@echo "Building project..."
	@fpm build

clean:
	@echo "Cleaning..."
	@rm -rf build/
	@find . -name "*.f90" -exec grep -l "GENERATED FROM .uf90" {} \; | xargs rm -f

run: build
	@fpm run

test: build
	@fpm test
```

### Git Hooks

**Pre-commit hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
# Auto-sync before commit

echo "Running uf90-sync..."
if command -v uf90-sync &> /dev/null; then
    uf90-sync
    
    # Stage any newly generated .f90 files
    git add -u '*.f90'
    
    echo "✓ Unicode files synced"
else
    echo "⚠ uf90-sync not found, skipping"
fi

exit 0
```

**Pre-push hook** (`.git/hooks/pre-push`):
```bash
#!/bin/bash
# Verify all .uf90 files are synced

echo "Verifying .uf90 sync status..."

if command -v uf90-sync &> /dev/null; then
    # Run sync
    uf90-sync
    
    # Check if any files changed
    if ! git diff --quiet '*.f90'; then
        echo "✗ Error: .uf90 files not synced with .f90"
        echo "  Run 'uf90-sync' and commit changes"
        exit 1
    fi
    
    echo "✓ All .uf90 files synced"
else
    echo "⚠ uf90-sync not found, skipping check"
fi

exit 0
```

Make hooks executable:
```bash
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

### CMake Integration

```cmake
# Find uf90-sync
find_program(UF90_SYNC uf90-sync)

if(UF90_SYNC)
    message(STATUS "Found uf90-sync: ${UF90_SYNC}")
    
    # Add custom target to sync .uf90 files
    add_custom_target(sync-unicode
        COMMAND ${UF90_SYNC}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "Syncing .uf90 files..."
    )
    
    # Make main target depend on sync
    add_dependencies(${PROJECT_NAME} sync-unicode)
else()
    message(WARNING "uf90-sync not found, .uf90 files won't be synced automatically")
endif()
```

### CI/CD Integration

See `.github/workflows/ci.yml` for complete example.

**Key points:**
1. Install uf90 in CI environment
2. Run `uf90-sync` before building
3. Verify generated files are correct

## Examples

### Example 1: Physics Simulation

```fortran
! src/physics.uf90
module physics_constants
  implicit none
  
  ! Physical constants with Greek symbols
  real, parameter :: π = 3.14159265358979_8
  real, parameter :: ε₀ = 8.854e-12_8        ! Vacuum permittivity
  real, parameter :: μ₀ = 1.257e-6_8         ! Vacuum permeability
  real, parameter :: c = 299792458.0_8       ! Speed of light
  
  ! Derived constants
  real, parameter :: α = 1.0_8 / 137.0_8    ! Fine structure constant
  
end module physics_constants

module electromagnetic_field
  use physics_constants
  implicit none
  
contains
  
  subroutine calculate_field(E, B, ε, μ)
    real, intent(out) :: E, B
    real, intent(in) :: ε, μ
    
    ! Maxwell's equations in simple form
    real :: λ, ν
    
    λ = 500.0e-9_8  ! Wavelength (500 nm)
    ν = c / λ       ! Frequency
    
    E = sqrt(2.0_8 * μ * c)  ! Electric field amplitude
    B = E / c                 ! Magnetic field amplitude
    
  end subroutine calculate_field
  
end module electromagnetic_field
```

**After uf90-sync:**
```fortran
! GENERATED FROM .uf90 SOURCE; DO NOT EDIT THIS .f90 FILE DIRECTLY
! SOURCE: src/physics.uf90

module physics_constants
  implicit none
  
  real, parameter :: pi = 3.14159265358979_8
  real, parameter :: epsilon_0 = 8.854e-12_8
  real, parameter :: mu_0 = 1.257e-6_8
  real, parameter :: c = 299792458.0_8
  real, parameter :: alpha = 1.0_8 / 137.0_8
  
end module physics_constants
! ...
```

### Example 2: Statistical Analysis

```fortran
! src/statistics.uf90
module statistics
  implicit none
  
contains
  
  subroutine calculate_moments(data, n, μ, σ², skew, kurt)
    integer, intent(in) :: n
    real, intent(in) :: data(n)
    real, intent(out) :: μ, σ², skew, kurt
    
    integer :: i
    real :: Σx, Σx², Σx³, Σx⁴
    
    ! Calculate sums
    Σx = sum(data)
    μ = Σx / real(n)
    
    Σx² = 0.0
    Σx³ = 0.0
    Σx⁴ = 0.0
    
    do i = 1, n
      Σx² = Σx² + (data(i) - μ)**2
      Σx³ = Σx³ + (data(i) - μ)**3
      Σx⁴ = Σx⁴ + (data(i) - μ)**4
    end do
    
    σ² = Σx² / real(n)
    skew = Σx³ / (real(n) * σ²**1.5)
    kurt = Σx⁴ / (real(n) * σ²**2)
    
  end subroutine calculate_moments
  
end module statistics
```

### Example 3: Matrix Operations

```fortran
! src/linalg.uf90
module linear_algebra
  implicit none
  
contains
  
  subroutine solve_system(A, b, x, n, λ)
    integer, intent(in) :: n
    real, intent(in) :: A(n,n), b(n)
    real, intent(out) :: x(n)
    real, intent(in), optional :: λ  ! Regularization parameter
    
    real :: A_reg(n,n)
    real :: λ_val
    integer :: i
    
    ! Use regularization if provided
    if (present(λ)) then
      λ_val = λ
    else
      λ_val = 0.0
    end if
    
    ! A_reg = A + λ*I
    A_reg = A
    do i = 1, n
      A_reg(i,i) = A_reg(i,i) + λ_val
    end do
    
    ! Solve (implementation omitted for brevity)
    call solve_linear_system(A_reg, b, x, n)
    
  end subroutine solve_system
  
end module linear_algebra
```

## Troubleshooting

### Common Issues

**Issue: "uf90-sync: command not found"**
```bash
# Solution: Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall
fpm install --prefix ~/.local
```

**Issue: "ERRO: nao achei fpm.toml"**
```bash
# Solution: Run from project root
cd /path/to/project/root
uf90-sync
```

**Issue: "ERRO: identificador ASCII reservado"**
```
Error: Don't use ASCII names like 'alpha', 'beta' in .uf90
Solution: Use Unicode symbols α, β instead
```

**Issue: "recusando sobrescrever .f90 nao-gerado"**
```
Error: .f90 file exists but wasn't generated by uf90
Solution: 
1. Backup your manual .f90 if needed
2. Remove it
3. Run uf90-sync again
```

**Issue: Python version doesn't work**
```bash
# Check Python version (need 3.6+)
python3 --version

# Try explicit invocation
python3 unicode_fortran_refactored.py file.uf90
```

### Getting Help

1. **Check documentation**: Read this guide thoroughly
2. **Search issues**: https://github.com/seu-usuario/uf90/issues
3. **Ask questions**: https://github.com/seu-usuario/uf90/discussions
4. **Report bugs**: Open a new issue with details

### Performance Tips

**For large projects:**
```bash
# Only sync changed files (default behavior)
uf90-sync

# Parallel build (FPM)
fpm build --flag "-j$(nproc)"
```

**For better compile times:**
- Keep .f90 files committed (skip translation in CI)
- Use ccache with your Fortran compiler
- Build in release mode for production

## Best Practices

1. **Always use .uf90 extension** for Unicode files
2. **Commit both .uf90 and .f90** to git
3. **Run uf90-sync before building**
4. **Use meaningful variable names** even with Unicode
5. **Add comments** explaining physics/math concepts
6. **Test generated .f90** compiles correctly

## Advanced Topics

### Custom Symbol Support

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to add new Unicode symbols.

### Integration with IDEs

**VS Code:**
- Install "Modern Fortran" extension
- Add .uf90 to Fortran file associations
- Use tasks.json to run uf90-sync

**Vim:**
```vim
" Add to .vimrc
autocmd BufWritePost *.uf90 !uf90-sync
```

**Emacs:**
```elisp
;; Add to init.el
(add-hook 'f90-mode-hook
  (lambda ()
    (add-hook 'after-save-hook 'uf90-sync nil t)))
```

---

For more help, see:
- [README.md](../README.md) - Project overview
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guide
- [SYMBOLS.md](SYMBOLS.md) - Complete symbol reference

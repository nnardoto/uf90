# Contributing to uf90

Thank you for considering contributing to uf90! 🎉

This document provides guidelines for contributing to the project.

## 🌟 Ways to Contribute

- 🐛 **Report bugs** - Open an issue with details
- 💡 **Suggest features** - Propose new Unicode symbols or features
- 📝 **Improve documentation** - Fix typos, add examples
- 🧪 **Add tests** - Increase test coverage
- 🔧 **Submit pull requests** - Fix bugs or add features
- 🌍 **Translation** - Help translate documentation

## 🚀 Getting Started

### Prerequisites

**For Fortran development:**
- Fortran compiler (gfortran 9+ or ifort)
- FPM (Fortran Package Manager)
- Git

**For Python development:**
- Python 3.8+
- Git

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/seu-usuario/uf90.git
cd uf90

# For Fortran development
fpm build

# For Python development
cd python
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 📋 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

**Fortran code:**
- Follow existing code style
- Add comments for complex logic
- Update relevant documentation

**Python code:**
- Follow PEP 8 style guide
- Add type hints where appropriate
- Add docstrings to functions/classes

### 3. Test Your Changes

**Fortran:**
```bash
fpm build
fpm test  # (when tests are implemented)

# Test manually
fpm install --prefix ~/.local
~/.local/bin/uf90-sync
```

**Python:**
```bash
cd python
python3 unicode_fortran_refactored.py ../examples/exemplo.uf90
python3 unicode_fortran_refactored.py --help
```

### 4. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add: Support for ∇ (nabla) operator"
git commit -m "Fix: Handle empty files correctly"
git commit -m "Docs: Update usage examples"
```

**Commit message format:**
- `Add:` - New feature
- `Fix:` - Bug fix
- `Docs:` - Documentation only
- `Test:` - Adding tests
- `Refactor:` - Code refactoring
- `Style:` - Formatting, no code change

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference any related issues (#123)
- List of changes made
- Screenshots if applicable

## 🎯 Coding Guidelines

### Fortran

```fortran
! Good: Clear names, proper indentation, comments
subroutine process_unicode_char(char, result)
  character(len=1), intent(in) :: char
  character(len=:), allocatable, intent(out) :: result
  
  ! Check if character is Greek letter
  if (is_greek_letter(char)) then
    result = translate_to_ascii(char)
  else
    result = char
  end if
end subroutine
```

**Guidelines:**
- Use `implicit none` in all modules/programs
- Maximum line length: 132 characters
- Indent with 2 spaces
- Use meaningful variable names
- Add comments for non-obvious code
- Use lowercase for keywords
- Use `intent` for all subroutine arguments

### Python

```python
# Good: Type hints, docstring, clear logic
def translate_unicode_char(char: str) -> str:
    """
    Translate a single Unicode character to ASCII.
    
    Args:
        char: Unicode character to translate
        
    Returns:
        ASCII replacement string
    """
    if is_greek_letter(char):
        return translate_to_ascii(char)
    return char
```

**Guidelines:**
- Follow PEP 8
- Maximum line length: 88 characters (Black formatter)
- Use type hints
- Write docstrings for public functions
- Use meaningful variable names
- Add comments for complex logic

## 🧪 Testing

### Adding Tests

We use different testing frameworks:

**Fortran (test-drive):**
```fortran
! test/test_translation.f90
program test_translation
  use testdrive, only : new_unittest, unittest_type, error_type, check
  use uf90_translation_rules, only : translate_identifier
  implicit none
  
  type(unittest_type), allocatable :: tests(:)
  
  tests = [ &
    new_unittest("alpha", test_alpha), &
    new_unittest("beta", test_beta) &
  ]
  
contains
  
  subroutine test_alpha(error)
    type(error_type), allocatable, intent(out) :: error
    character(len=:), allocatable :: result
    
    result = translate_identifier("α")
    call check(error, result, "alpha")
  end subroutine
  
end program
```

**Python (pytest):**
```python
# python/test_translator.py
import pytest
from unicode_fortran_refactored import UnicodeTranslator

def test_alpha_translation():
    translator = UnicodeTranslator()
    result = translator.translate("α")
    assert result == "alpha"

def test_beta_translation():
    translator = UnicodeTranslator()
    result = translator.translate("β")
    assert result == "beta"
```

### Running Tests

```bash
# Fortran
fpm test

# Python
cd python
pytest test_translator.py
```

## 📝 Documentation

### Adding New Unicode Symbols

When adding support for new Unicode symbols:

1. **Update the mapping tables:**
   - Fortran: `src/uf90_translation_rules.f90`
   - Python: `unicode_fortran_refactored.py` → `MappingRegistry`

2. **Update documentation:**
   - Add to `docs/SYMBOLS.md`
   - Update examples if relevant

3. **Add tests:**
   - Test translation works correctly
   - Test edge cases (e.g., consecutive symbols)

### Example: Adding Nabla (∇)

**Fortran:**
```fortran
! In match_greek_at()
if (starts_with(s, pos, "∇")) then
  repl="nabla"
  keylen=len("∇")
  return
end if
```

**Python:**
```python
# In MappingRegistry._initialize_mappings()
calculus_symbols = [
    # ... existing ...
    ('∇', 'nabla', 'nabla/gradient'),
]
```

## 🐛 Reporting Bugs

Good bug reports include:

1. **Clear title** - Summarize the issue
2. **Steps to reproduce** - Exact steps to trigger the bug
3. **Expected behavior** - What should happen
4. **Actual behavior** - What actually happens
5. **Environment** - OS, compiler version, FPM version
6. **Code sample** - Minimal example that reproduces the issue

**Example:**
```markdown
## Bug: uf90-sync crashes with nested Greek letters

**Environment:**
- OS: Ubuntu 22.04
- FPM: 0.9.0
- gfortran: 11.3.0

**Steps to reproduce:**
1. Create file with: `real :: α_β`
2. Run `uf90-sync`

**Expected:** Translates to `real :: alpha_beta`
**Actual:** Segmentation fault

**Code sample:**
```fortran
program test
  real :: α_β
end program
```
```

## 💡 Feature Requests

Good feature requests include:

1. **Use case** - Why is this needed?
2. **Proposed solution** - How should it work?
3. **Alternatives** - Other ways to achieve this?
4. **Examples** - Show how it would be used

## 🔄 Pull Request Process

1. **Update documentation** if you change functionality
2. **Add tests** for new features
3. **Update CHANGELOG** (if exists)
4. **Ensure CI passes** - All tests must pass
5. **Request review** from maintainers

### PR Checklist

Before submitting, verify:

- [ ] Code follows style guidelines
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] Commit messages are clear
- [ ] No debugging code left in
- [ ] PR description is complete

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment.

### Expected Behavior

- Be respectful and considerate
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory comments
- Personal attacks
- Publishing private information
- Other unprofessional conduct

### Reporting

Report unacceptable behavior to: community@uf90.dev

## 📫 Questions?

- **General questions**: [GitHub Discussions](https://github.com/seu-usuario/uf90/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/seu-usuario/uf90/issues)
- **Email**: community@uf90.dev

## 🙏 Thank You!

Your contributions make uf90 better for everyone. We appreciate your time and effort! ⭐

---

**Happy coding!** 🚀

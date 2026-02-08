# Python Implementation

This directory contains the standalone Python implementation of uf90.

## Features

- ✅ **Portable** - Runs anywhere Python 3.6+ is installed
- ✅ **Single file** - Easy to distribute
- ✅ **Well documented** - Extensive comments and docstrings
- ✅ **Object-oriented** - Clean, maintainable code structure
- ✅ **Type hints** - Better IDE support and type checking
- ✅ **CLI + API** - Use from command line or import as library

## Quick Start

```bash
# Make executable
chmod +x unicode_fortran_refactored.py

# Translate a file
./unicode_fortran_refactored.py myfile.uf90

# See all options
./unicode_fortran_refactored.py --help
```

## Installation Options

### Option 1: Direct Use (No Installation)

```bash
# Download
wget https://raw.githubusercontent.com/seu-usuario/uf90/main/python/unicode_fortran_refactored.py

# Use directly
python3 unicode_fortran_refactored.py file.uf90
```

### Option 2: Global Install

```bash
# Install to /usr/local/bin
sudo cp unicode_fortran_refactored.py /usr/local/bin/uf90-py
sudo chmod +x /usr/local/bin/uf90-py

# Use from anywhere
uf90-py file.uf90
```

### Option 3: User Install

```bash
# Install to ~/.local/bin
cp unicode_fortran_refactored.py ~/.local/bin/uf90-py
chmod +x ~/.local/bin/uf90-py

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"

# Use from anywhere
uf90-py file.uf90
```

## Command-Line Usage

```bash
# Basic translation
uf90-py input.uf90                    # Generates input.f90

# Specify output file
uf90-py input.uf90 -o output.f90

# Translate Unicode in comments too
uf90-py input.uf90 --no-preserve

# Verbose mode (show statistics)
uf90-py -v input.uf90

# Generate mapping reference table
uf90-py --generate-table              # Creates unicode_mapping.txt
```

## Python API Usage

The module can be imported and used programmatically:

```python
from unicode_fortran_refactored import (
    UnicodeTranslator,
    FileProcessor,
    MappingRegistry,
    SubscriptProcessor
)

# Example 1: Translate a string
translator = UnicodeTranslator(preserve_comments=True)
fortran_code = "real :: α, β, γ"
translated = translator.translate(fortran_code)
print(translated)  # "real :: alpha, beta, gamma"

# Example 2: Process a file
processor = FileProcessor(translator, verbose=True)
output_path = processor.process_file("input.uf90", "output.f90")

# Example 3: Access symbol mappings
registry = MappingRegistry()
mapping = registry.get_mapping('α')
print(f"{mapping.unicode_char} → {mapping.ascii_replacement}")

# Example 4: Get all supported symbols
all_symbols = registry.get_all_unicode_chars()
print(f"Supports {len(all_symbols)} Unicode symbols")

# Example 5: Process subscripts
text_with_subscripts = "x₁₂ = y₃₄"
processed = SubscriptProcessor.process(text_with_subscripts)
print(processed)  # "x_12 = y_34"
```

## Architecture

The code is organized into several classes:

```
unicode_fortran_refactored.py
├── UnicodeMapping (dataclass)
│   └── Represents one Unicode → ASCII mapping
│
├── MappingRegistry
│   ├── Centralizes all mappings
│   ├── Organizes by category
│   └── Provides lookup functions
│
├── SubscriptProcessor
│   └── Handles consecutive subscripts (₁₂ → _12)
│
├── UnicodeTranslator
│   ├── Main translation logic
│   ├── Preserves comments (optional)
│   └── Processes text line-by-line
│
├── FileProcessor
│   ├── File I/O operations
│   ├── Determines output paths
│   └── Shows statistics (verbose mode)
│
├── MappingTableGenerator
│   └── Generates reference documentation
│
└── CLI (main function)
    └── Command-line interface
```

## Code Quality

- **Lines of code**: ~700
- **Comments**: ~45% (well documented!)
- **Type hints**: Yes (Python 3.6+ compatible)
- **Docstrings**: All public functions
- **Dependencies**: None (pure stdlib)

## Comparison with Fortran Version

| Feature | Python | Fortran |
|---------|--------|---------|
| **Speed** | Good (2-3s for 10k lines) | Excellent (<1s) |
| **Portability** | Excellent (any OS with Python) | Good (after compile) |
| **Easy to modify** | Excellent (OOP, dynamic) | Good (needs recompile) |
| **FPM integration** | External script | Native |
| **Installation** | Copy one file | Needs FPM + compiler |

**Use Python when:**
- You don't have FPM installed
- You want maximum portability
- You need to modify/extend the code
- You're doing one-off translations
- You prefer Python over Fortran

**Use Fortran when:**
- You have an FPM project
- You need maximum performance
- You want native integration
- You're building frequently

See [docs/COMPARISON.md](../docs/COMPARISON.md) for detailed analysis.

## Examples

### Example 1: Batch Processing

```python
from pathlib import Path
from unicode_fortran_refactored import UnicodeTranslator, FileProcessor

translator = UnicodeTranslator()
processor = FileProcessor(translator)

# Process all .uf90 files in a directory
source_dir = Path("src")
for uf90_file in source_dir.glob("**/*.uf90"):
    f90_file = uf90_file.with_suffix(".f90")
    processor.process_file(str(uf90_file), str(f90_file))
    print(f"✓ {uf90_file.name} → {f90_file.name}")
```

### Example 2: Custom Mapping

```python
from unicode_fortran_refactored import MappingRegistry, UnicodeMapping

# Get registry
registry = MappingRegistry()

# Add custom mapping (would need to modify source for persistence)
custom_mapping = UnicodeMapping('ℏ', 'hbar', 'Reduced Planck constant')

# Use in translation
# (Note: This example shows the concept; 
#  actual implementation would require modifying _initialize_mappings)
```

### Example 3: Integration with Build System

```python
#!/usr/bin/env python3
"""Build script with automatic Unicode translation."""

import subprocess
from unicode_fortran_refactored import FileProcessor, UnicodeTranslator

def sync_unicode_files():
    """Sync all .uf90 files."""
    translator = UnicodeTranslator()
    processor = FileProcessor(translator)
    
    # Find and process all .uf90 files
    from pathlib import Path
    for uf90 in Path("src").rglob("*.uf90"):
        f90 = uf90.with_suffix(".f90")
        if not f90.exists() or uf90.stat().st_mtime > f90.stat().st_mtime:
            processor.process_file(str(uf90), str(f90))

def build():
    """Build the project."""
    sync_unicode_files()
    subprocess.run(["fpm", "build"], check=True)

if __name__ == "__main__":
    build()
```

## Testing

While the main repository has comprehensive tests, you can do quick tests:

```bash
# Test basic translation
echo 'program test
  real :: α
end program' > test.uf90

python3 unicode_fortran_refactored.py test.uf90
cat test.f90

# Should see "real :: alpha"
```

## Performance

Approximate performance on a typical laptop:

| File Size | Lines | Time |
|-----------|-------|------|
| 1 KB | ~50 | <0.1s |
| 10 KB | ~500 | ~0.2s |
| 100 KB | ~5000 | ~2s |
| 1 MB | ~50000 | ~20s |

For large projects with hundreds of files, consider using the Fortran version for better performance.

## Troubleshooting

**Issue: "Permission denied"**
```bash
chmod +x unicode_fortran_refactored.py
```

**Issue: "No module named 'unicode_fortran_refactored'"**
```bash
# Make sure you're in the right directory
cd /path/to/uf90/python
python3 unicode_fortran_refactored.py file.uf90
```

**Issue: "Python version too old"**
```bash
# Need Python 3.6+
python3 --version

# Update Python if needed
```

## Contributing

To contribute to the Python implementation:

1. Modify `unicode_fortran_refactored.py`
2. Test thoroughly with various .uf90 files
3. Ensure consistency with Fortran version output
4. Add appropriate comments/docstrings
5. Update this README if needed

See [CONTRIBUTING.md](../CONTRIBUTING.md) for general contribution guidelines.

## License

MIT License - See [LICENSE](../LICENSE) file.

## See Also

- [Main README](../README.md) - Project overview
- [Usage Guide](../docs/USAGE.md) - Detailed usage instructions
- [Symbol Reference](../docs/SYMBOLS.md) - All supported symbols
- [Fortran Implementation](../src/) - Native Fortran version

---

**Questions?** Open an issue or discussion on GitHub!

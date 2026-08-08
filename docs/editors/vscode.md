# VS Code and fortls

[Português (Brasil)](../pt-BR/editors/vscode.md)

This integration was tested with Modern Fortran 4.0.0 and fortls 3.2.2.

Install the [Modern Fortran extension](https://marketplace.visualstudio.com/items?itemName=fortran-lang.linter-gfortran)
and make sure `fortls` is available to it. Then generate the project-specific
fortls configuration from the directory containing `fpm.toml`:

```bash
uf90 fortls-config
```

The generated `.uf90-fortls.json` adds `.f90u` to the indexed suffixes and
excludes only the corresponding generated `.f90` files. Handwritten `.f90`
sources remain indexed. Run the command again after adding or removing a
`.f90u` file.

Add these workspace settings to `.vscode/settings.json`:

```json
{
  "files.associations": {
    "*.f90u": "FortranFreeForm"
  },
  "fortran.fortls.configure": ".uf90-fortls.json",
  "fortran.linter.compiler": "Disabled"
}
```

The compiler linter is disabled because Fortran compilers receive the Unicode
source before `uf90` can translate it. Compilation diagnostics remain available
through `fpm uf90 build`.

## Current behavior

With this configuration, syntax highlighting, document symbols, diagnostics,
and navigation between project files work on `.f90u` sources. Hover,
definitions, and references also work for identifiers that begin with an ASCII
letter and contain Unicode subscripts or superscripts, such as `E₀`.

In fortls 3.2.2, those operations do not resolve identifiers that begin with a
Greek letter, such as `α` or `Δt`. The parser still indexes these declarations,
but this limitation means that the current integration is partial rather than
full language-server support.

The proposed next step is a bidirectional proxy that lets fortls analyze the
generated `.f90` while the editor continues to display `.f90u`. See the
[uf90 0.2 design proposal](../design/fortls-proxy-v0.2.md). It is not
implemented in 0.1.1.

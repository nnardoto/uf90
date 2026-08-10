# VS Code and uf90-ls

[Português (Brasil)](../pt-BR/editors/vscode.md)

The experimental 0.2 integration uses `uf90-ls` as a bidirectional proxy. The
editor opens `.f90u` sources while fortls indexes their generated `.f90` pairs.
It has been tested with Modern Fortran 4.0.0 and fortls 3.2.2.

## Install the development version

From a checkout of the 0.2 branch:

```bash
pipx install --force --editable '.[lsp]'
uf90-ls --version
```

After 0.2 is published, the equivalent release installation is
`pipx install 'uf90[lsp]'`.

The last command should print `3.2.2`. Injecting fortls into the uf90 pipx
environment also lets GUI-launched editors find it when they do not inherit
your shell `PATH`.

## Workspace settings

Install the [Modern Fortran extension](https://marketplace.visualstudio.com/items?itemName=fortran-lang.linter-gfortran),
then generate the workspace settings from its root:

```bash
uf90 editor-config vscode -o .vscode/settings.json
```

The command detects the absolute `uf90-ls` path. It refuses to replace an
existing file; if `.vscode/settings.json` already exists, run
`uf90 editor-config vscode` without `-o` and merge the printed keys. The
generated content is:

```json
{
  "files.associations": {
    "*.f90u": "FortranFreeForm"
  },
  "fortran.fortls.path": "/absolute/path/to/uf90-ls",
  "fortran.fortls.configure": "",
  "fortran.fortls.incrementalSync": false,
  "fortran.fortls.notifyInit": true,
  "fortran.linter.compiler": "Disabled"
}
```

Use `--server /custom/path/to/uf90-ls` when automatic detection is not suitable.
Full-document synchronization is required by the current proxy.

Do not select `.uf90-fortls.json` in proxy mode. That legacy configuration
indexes `.f90u` directly, while `uf90-ls` needs fortls to index generated
`.f90` files. The compiler linter remains disabled because a Fortran compiler
cannot consume the Unicode source directly; compilation diagnostics remain
available through `fpm uf90 build`.

## What to test

Open `examples/06_oscillator` as the workspace and use the `.f90u` files:

- hover over `system%ω` and `system%Δt`;
- go to their declarations in `src/oscillator.f90u`;
- find references and confirm every paired result points to `.f90u`;
- make an unsaved edit and confirm navigation sees it without changing the
  adjacent `.f90` on disk.
- type `\alpha` and accept the `α` completion; use `Ctrl+Space` if the menu is
  not already visible. `\partial` and `\nabla` insert `∂` and `∇`.
- accept completion for `x_n`, `T_{100}`, or `A_ij` to insert `xₙ`, `T₁₀₀`,
  or `Aᵢⱼ`. The `_` and closing `}` characters trigger these suggestions.

Read-only navigation, symbols, diagnostics, and Unicode names in hover are
implemented. Unicode symbol input completion is provided locally by `uf90-ls`;
fortls semantic completion, signature help, rename, code actions, and
formatting remain disabled until their edits and presentation text can be
translated safely.

If the server does not attach, run **Fortran: Restart the Fortran Language
Server** and inspect **View: Output → Modern Fortran**. Also confirm that
`uf90-ls --version` works in a terminal.

## Legacy direct-fortls mode

Without the 0.2 proxy, `uf90 fortls-config` generates the partial 0.1.1 setup
that indexes `.f90u` directly. It supports identifiers such as `E₀`, but fortls
3.2.2 cannot resolve names beginning with Greek letters in that mode.

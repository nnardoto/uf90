from __future__ import annotations

import json
from pathlib import Path
import shutil


EDITORS = ("vscode", "neovim")


def find_uf90_ls() -> str:
    executable = shutil.which("uf90-ls")
    return str(Path(executable).absolute()) if executable else "uf90-ls"


def render_editor_config(editor: str, server: str | None = None) -> str:
    executable = find_uf90_ls() if server is None else server
    if editor == "vscode":
        settings = {
            "files.associations": {"*.f90u": "FortranFreeForm"},
            "fortran.fortls.path": executable,
            "fortran.fortls.configure": "",
            "fortran.fortls.incrementalSync": False,
            "fortran.fortls.notifyInit": True,
            "fortran.linter.compiler": "Disabled",
        }
        return json.dumps(settings, indent=2, ensure_ascii=False) + "\n"
    if editor == "neovim":
        lua_executable = executable.replace("\\", "/").replace("'", "\\'")
        return f"""vim.filetype.add({{
  extension = {{
    f90u = 'fortran',
  }},
}})

vim.lsp.config('uf90_ls', {{
  cmd = {{ '{lua_executable}', '--disable_autoupdate' }},
  filetypes = {{ 'fortran' }},
  root_markers = {{ 'fpm.toml', '.git' }},
}})

vim.api.nvim_create_autocmd('LspAttach', {{
  callback = function(args)
    local client = vim.lsp.get_client_by_id(args.data.client_id)
    if client and client.name == 'uf90_ls' then
      vim.lsp.completion.enable(true, client.id, args.buf, {{ autotrigger = true }})
      vim.keymap.set('i', '<C-Space>', vim.lsp.completion.get, {{ buffer = args.buf }})
    end
  end,
}})

vim.lsp.enable('uf90_ls')
"""
    raise ValueError(f"unsupported editor: {editor}")


def write_editor_config(
    editor: str,
    output: Path,
    *,
    server: str | None = None,
    force: bool = False,
) -> Path:
    output = Path(output)
    if output.exists() and not force:
        raise FileExistsError(
            f"{output} já existe; use --force somente se quiser substituí-lo"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_editor_config(editor, server), encoding="utf-8")
    return output

# VS Code e uf90-ls

[English](../../editors/vscode.md)

A integração experimental 0.2 usa `uf90-ls` como proxy bidirecional. O editor
abre os fontes `.f90u`, enquanto o fortls indexa os pares `.f90` gerados. Ela
foi testada com Modern Fortran 4.0.0 e fortls 3.2.2.

## Instalação da versão em desenvolvimento

A partir de um checkout da branch 0.2:

```bash
pipx install --force --editable '.[lsp]'
uf90-ls --version
```

Depois da publicação da versão 0.2, a instalação equivalente será
`pipx install 'uf90[lsp]'`.

O último comando deve imprimir `3.2.2`. Injetar o fortls no ambiente pipx do
uf90 também permite que editores iniciados pela interface gráfica o encontrem
quando não herdam o `PATH` do shell.

## Configuração do workspace

Instale a [extensão Modern Fortran](https://marketplace.visualstudio.com/items?itemName=fortran-lang.linter-gfortran)
e gere a configuração a partir da raiz do workspace:

```bash
uf90 editor-config vscode -o .vscode/settings.json
```

O comando detecta o caminho absoluto de `uf90-ls`. Ele se recusa a substituir
um arquivo existente; se `.vscode/settings.json` já existir, execute
`uf90 editor-config vscode` sem `-o` e incorpore as chaves impressas. O conteúdo
gerado é:

```json
{
  "files.associations": {
    "*.f90u": "FortranFreeForm"
  },
  "fortran.fortls.path": "/caminho/absoluto/para/uf90-ls",
  "fortran.fortls.configure": "",
  "fortran.fortls.incrementalSync": false,
  "fortran.fortls.notifyInit": true,
  "fortran.linter.compiler": "Disabled"
}
```

Use `--server /caminho/personalizado/uf90-ls` se a detecção automática não for
adequada. A versão atual do proxy requer sincronização integral do documento.

Não selecione `.uf90-fortls.json` no modo proxy. Essa configuração legada
indexa `.f90u` diretamente, enquanto `uf90-ls` precisa que o fortls indexe os
arquivos `.f90` gerados. O linter do compilador permanece desativado porque um
compilador Fortran não consome diretamente o fonte Unicode; os diagnósticos de
compilação continuam disponíveis por meio de `fpm uf90 build`.

## O que testar

Abra `examples/06_oscillator` como workspace e use os arquivos `.f90u`:

- passe o cursor sobre `system%ω` e `system%Δt`;
- navegue até suas declarações em `src/oscillator.f90u`;
- procure referências e confirme que todo resultado pareado aponta para
  `.f90u`;
- faça uma alteração sem salvar e confirme que a navegação a reconhece sem
  modificar o `.f90` adjacente no disco.
- digite `\alpha` e aceite a conclusão `α`; use `Ctrl+Space` se o menu não
  estiver visível. `\partial` e `\nabla` inserem `∂` e `∇`.

Navegação somente para leitura, símbolos, diagnósticos e nomes Unicode no
hover estão implementados. A conclusão para inserir símbolos Unicode é fornecida
localmente pelo `uf90-ls`; conclusão semântica do fortls, ajuda de assinatura,
rename, ações de código e formatação permanecem desativados até que suas
edições e seu texto de apresentação possam ser traduzidos com segurança.

Se o servidor não conectar, execute **Fortran: Restart the Fortran Language
Server** e inspecione **View: Output → Modern Fortran**. Confirme também que
`uf90-ls --version` funciona em um terminal.

## Modo legado com fortls direto

Sem o proxy 0.2, `uf90 fortls-config` gera a configuração parcial da versão
0.1.1, que indexa `.f90u` diretamente. Ela suporta identificadores como `E₀`,
mas o fortls 3.2.2 não resolve nomes iniciados por letras gregas nesse modo.

# VS Code e fortls

[English](../../editors/vscode.md)

Esta integração foi testada com Modern Fortran 4.0.0 e fortls 3.2.2.

Instale a [extensão Modern Fortran](https://marketplace.visualstudio.com/items?itemName=fortran-lang.linter-gfortran)
e certifique-se de que o `fortls` esteja disponível para ela. Depois, gere a
configuração específica do projeto no diretório que contém `fpm.toml`:

```bash
uf90 fortls-config
```

O arquivo `.uf90-fortls.json` acrescenta `.f90u` às extensões indexadas e
exclui somente os arquivos `.f90` gerados correspondentes. Fontes `.f90`
escritos manualmente continuam no índice. Execute o comando novamente depois
de adicionar ou remover um arquivo `.f90u`.

Adicione estas configurações a `.vscode/settings.json`:

```json
{
  "files.associations": {
    "*.f90u": "FortranFreeForm"
  },
  "fortran.fortls.configure": ".uf90-fortls.json",
  "fortran.linter.compiler": "Disabled"
}
```

O linter do compilador é desativado porque o compilador Fortran recebe o fonte
Unicode antes que o `uf90` possa traduzi-lo. Os diagnósticos de compilação
continuam disponíveis por meio de `fpm uf90 build`.

## Comportamento atual

Com essa configuração, realce de sintaxe, símbolos do documento, diagnósticos
e navegação entre arquivos do projeto funcionam nos fontes `.f90u`. Hover,
definições e referências também funcionam para identificadores que começam com
uma letra ASCII e contêm subscritos ou sobrescritos Unicode, como `E₀`.

No fortls 3.2.2, essas operações não resolvem identificadores iniciados por uma
letra grega, como `α` ou `Δt`. O parser ainda indexa essas declarações, mas essa
limitação significa que a integração atual é parcial, não um suporte completo
do servidor de linguagem.

O próximo passo proposto é um proxy bidirecional: o fortls analisa o `.f90`
gerado enquanto o editor continua exibindo o `.f90u`. Consulte a
[proposta para o uf90 0.2](../design/fortls-proxy-v0.2.md). Ela não está
implementada na versão 0.1.1.

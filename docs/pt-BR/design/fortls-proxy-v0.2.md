# Proposta: proxy do fortls para o uf90 0.2

[English](../../design/fortls-proxy-v0.2.md)

Estado: implementação em andamento na branch de desenvolvimento 0.2.

Este documento registra o caminho pretendido para o suporte a editores depois
do uf90 0.1.1. Ele contém o contexto necessário para iniciar a implementação em
uma nova sessão de desenvolvimento.

## Objetivo

Usar o fortls para analisar os arquivos `.f90` ASCII gerados enquanto o usuário
continua abrindo e editando os arquivos `.f90u`. Um pequeno proxy de servidor de
linguagem traduz URIs e posições nas duas direções:

```text
VS Code ou outro cliente LSP (.f90u)
                  <->
               uf90-ls
        traduz texto, URIs e posições
                  <->
              fortls (.f90)
```

O proxy deve fazer hover, definições, referências e diagnósticos funcionarem
para identificadores que o fortls atualmente não resolve diretamente em
`.f90u`, inclusive nomes iniciados por letras gregas.

## Ponto de partida na versão 0.1.1

A integração 0.1.1 acrescenta `.f90u` às extensões do fortls e exclui os `.f90`
gerados correspondentes. Os testes com Modern Fortran 4.0.0 e fortls 3.2.2
mostraram que:

- parsing, símbolos do documento e diagnósticos funcionam em `.f90u`;
- a navegação funciona para identificadores como `E₀`, iniciados em ASCII;
- hover, definições e referências não resolvem nomes iniciados por letras
  gregas, como `α` e `Δt`;
- indexar simultaneamente um `.f90u` e seu `.f90` gerado pode levar a navegação
  ao arquivo gerado.

A configuração atual continua útil como integração parcial documentada. O proxy
é uma funcionalidade separada, proposta para a versão 0.2, e não uma correção a
ser escondida no escopo da 0.1.1.

## Integração proposta

O pacote deverá fornecer um executável chamado `uf90-ls`. O Modern Fortran pode
iniciá-lo por sua configuração existente para o caminho do servidor:

```json
{
  "files.associations": {
    "*.f90u": "FortranFreeForm"
  },
  "fortran.fortls.path": "uf90-ls",
  "fortran.linter.compiler": "Disabled"
}
```

`uf90-ls` fala JSON-RPC/LSP pela entrada e saída padrão e inicia o processo real
do `fortls` por trás. Ele precisa repassar os argumentos de linha de comando do
fortls e oferecer uma forma explícita de selecionar o executável subjacente sem
iniciar a si próprio recursivamente, por exemplo `UF90_FORTLS_PATH`.

Esse desenho não depende do editor. O VS Code será o primeiro cliente testado,
mas a tradução pertence ao proxy, não a uma extensão exclusiva do VS Code.

## Ciclo de vida dos documentos

Ao iniciar, o proxy deve sincronizar o projeto para que o fortls indexe um
workspace ASCII completo. Para cada par:

```text
src/model.f90u <-> src/model.f90
```

A primeira implementação pode seguir este ciclo:

1. Executar o equivalente a `uf90 sync` antes de iniciar o fortls.
2. Converter `textDocument/didOpen`, trocando URI e texto `.f90u` pelo URI
   `.f90` correspondente e pelo texto traduzido.
3. Traduzir o documento completo em memória a cada `textDocument/didChange`.
   A sincronização integral é preferível na primeira versão.
4. Gravar o `.f90` gerado em `textDocument/didSave`, mantendo a entrada usada
   pelo fpm igual ao fonte `.f90u` salvo.
5. Repassar `textDocument/didClose` com o URI correspondente.

O conteúdo ainda não salvo deve ser enviado ao fortls somente em memória. Ele
não deve virar silenciosamente entrada do compilador antes que o `.f90u` seja
salvo.

Arquivos `.f90` escritos manualmente não possuem um `.f90u` correspondente e
passam pelo proxy sem modificação.

Para receber documentos completos, o proxy deverá ajustar a capacidade
`textDocumentSync` devolvida durante `initialize`, mesmo que o fortls anuncie
sincronização incremental ao proxy.

## Mapas de origem

A tradução preserva os limites físicos das linhas, portanto os números de linha
normalmente não mudam. As colunas mudam:

```text
.f90u: real :: α
.f90:  real :: uc_alpha
```

O tradutor deverá produzir um mapa de origem ao mesmo tempo que o texto ASCII.
Reconstruir as posições posteriormente seria frágil. Para cada linha traduzida,
o mapa deve relacionar os limites dos caracteres no fonte e na saída, além dos
URIs correspondentes.

As posições do LSP usam uma codificação negociada. O VS Code normalmente usa
UTF-16, enquanto índices de strings Python contam pontos de código Unicode. As
funções de conversão devem considerar explicitamente a codificação negociada,
sem assumir que um índice Python equivale à coluna do LSP.

A API existente `translate_text()` deve continuar compatível. Uma nova API
interna pode retornar algo semelhante a:

```python
TranslationResult(
    text=generated_text,
    source_map=source_map,
)
```

O mapa precisa funcionar nas duas direções e definir como uma posição no meio
de um token expandido volta ao token Unicode original.

## Tradução das mensagens LSP

Mensagens do cliente para o servidor devem trocar URIs `.f90u` por `.f90` e
converter posições ou intervalos para as coordenadas geradas. Mensagens do
servidor para o cliente fazem a transformação inversa.

A implementação deve usar tratadores tipados e específicos para cada método,
não uma substituição irrestrita de todo objeto que contenha `uri`, `line` ou
`character`. Esses campos têm significados diferentes conforme o método LSP.

### Marco 1: navegação somente para leitura

O primeiro marco útil deve cobrir:

- encaminhamento de inicialização e encerramento;
- notificações de abertura, alteração integral, salvamento e fechamento;
- hover;
- definição, declaração, definição de tipo e implementação;
- referências;
- símbolos do documento e do workspace;
- diagnósticos publicados pelo fortls.

`Location`, `LocationLink`, `Range`, `DocumentSymbol` e estruturas relacionadas
devem apontar para `.f90u` apenas quando existir um par conhecido. Localizações
em fontes Fortran manuais ou bibliotecas externas permanecem `.f90`.

### Marco 2: autocompletar e assinaturas

A versão 0.2 oferece uma camada deliberadamente menor para entrada: o proxy
trata localmente comandos gregos no estilo LaTeX, como `\alpha`, e devolve um
`TextEdit` que substitui o comando por `α`. Isso não depende da identidade de
símbolos do fortls e, portanto, é seguro nos dois editores suportados.

Rótulos de sugestões, texto inserido e intervalos de `TextEdit` podem conter
nomes ASCII gerados como `uc_alpha`. Convertê-los de volta requer um mapa de
símbolos do projeto além dos mapas de posição. Assinaturas e o conteúdo do hover
podem exigir a mesma conversão de apresentação. Esse autocomplete semântico
mais amplo vindo do fortls permanece desativado.

### Marco 3: operações de edição

Rename, code actions e workspace edits podem alterar vários arquivos. Devem
permanecer desativados ou passar diretamente apenas para `.f90` manuais até que
cada edição possa ser traduzida com segurança para `.f90u`. Nenhuma operação
pode editar um `.f90` gerado e apresentar essa edição como bem-sucedida no fonte
Unicode.

## Identidade de nomes e colisões

O proxy torna visível uma preocupação já existente: identificadores Unicode e
ASCII distintos podem ser normalizados para o mesmo nome Fortran. Mapas de
posição bastam para navegar até uma ocorrência existente, mas autocomplete e
rename exigem identidade inequívoca.

Antes de habilitar operações de edição, o uf90 deverá detectar colisões em cada
escopo Fortran ou, conservadoramente, no projeto inteiro. Isso inclui um nome
Unicode e um nome ASCII manual que produzam a mesma grafia normalizada.

## Política para arquivos gerados

A implementação inicial recomendada deve reutilizar os `.f90` adjacentes já
consumidos pelo fpm. Isso evita manter um segundo workspace oculto e preserva a
descoberta de módulos usada na compilação.

Um cache separado, como `.uf90/lsp/`, só deve ser considerado se os arquivos
adjacentes causarem problemas concretos de edição ou concorrência. Uma árvore
oculta também precisaria espelhar fontes manuais, caminhos de include e a
estrutura do projeto.

Com o proxy ativo, o fortls deverá indexar os `.f90` gerados, não os `.f90u`.
Portanto, o comportamento de `fortls-config` da versão 0.1.1 não é a
configuração final do modo proxy.

## Comportamento diante de falhas

- Se a tradução falhar, publicar um diagnóstico no `.f90u` e não enviar texto
  gerado antigo como se estivesse atualizado.
- Se o fortls não existir ou encerrar, mostrar um erro claro e preservar seu
  status de saída quando possível.
- Logs devem ir para a saída de erro ou para arquivo; a saída padrão é reservada
  às mensagens JSON-RPC.
- O proxy deve impedir recursão ao localizar o executável real do fortls.
- Cancelamentos e identificadores de requisição devem ser encaminhados sem
  reordenação.

## Critérios de aceite para a versão 0.2.0

Usar tanto um servidor LSP falso e determinístico quanto um job fixado em uma
versão do fortls. Verificar pelo menos:

- conversão de URI para pares `.f90u`/`.f90`;
- URIs inalterados para `.f90` manuais e externos;
- mapeamento de posições antes, dentro e depois de expansões gregas, subscritas
  e sobrescritas;
- posições UTF-16, inclusive caracteres fora do BMP em comentários ou strings;
- definição e referências entre arquivos para nomes iniciados por letras
  gregas;
- intervalos de diagnóstico convertidos para `.f90u`;
- alterações integrais ainda não salvas sem atualizar no disco a entrada do
  compilador;
- encerramento limpo, cancelamento e falha do subprocesso fortls;
- execução em Linux, macOS e Windows pelo `uf90-ls` instalado pelo pipx.

O exemplo do oscilador é um bom teste ponta a ponta: contém membros iniciados
por letras gregas (`ω`, `Δt`) e identificadores iniciados em ASCII com
subscritos Unicode (`E₀`).

## Fora do escopo inicial

- implementar um novo parser ou servidor de linguagem Fortran;
- manter um fork do fortls;
- substituir o Modern Fortran;
- fornecer diagnósticos do compilador diretamente sobre `.f90u` não salvo;
- oferecer rename ou workspace edits arbitrários antes que as edições nas duas
  direções sejam comprovadamente seguras;
- depender de LLVM ou MLIR.

## Decisões ainda abertas

Resolver durante o primeiro experimento de implementação:

1. Se sincronização integral basta para 0.2.0 ou se a incremental será
   necessária posteriormente.
2. O mecanismo exato para selecionar o executável real do fortls.
3. Se hover e autocomplete já devem apresentar nomes Unicode em 0.2.0 ou se o
   primeiro compromisso será apenas navegação e intervalos corretos.
4. O rigor necessário para detectar colisões antes de habilitar autocomplete e
   rename.
5. Se o modo proxy substitui `uf90 fortls-config` ou entra como modo explícito
   separado durante a transição.

## Ordem sugerida de implementação

1. Refatorar a tradução para emitir opcionalmente mapas bidirecionais e testá-los
   sem envolver LSP.
2. Implementar o enquadramento JSON-RPC e o encaminhamento transparente do
   processo fortls.
3. Acrescentar tradução de URIs e sincronização integral dos documentos.
4. Adicionar hover, definição, referências, símbolos e diagnósticos, um método
   por vez.
5. Criar um teste ponta a ponta com o fortls real e o exemplo do oscilador.
6. Documentar a configuração experimental do VS Code e empacotar `uf90-ls` na
   distribuição já instalável pelo pipx.
7. Considerar autocomplete, assinaturas e rename somente depois da camada de
   leitura estar estável.

Referências relevantes:

- [Language Server Protocol](https://microsoft.github.io/language-server-protocol/)
- [Guia de servidores de linguagem do VS Code](https://code.visualstudio.com/api/language-extensions/language-server-extension-guide)
- [Opções de configuração do fortls](https://fortls.fortran-lang.org/options.html)

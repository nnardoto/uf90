# Exemplos progressivos

Cada subdiretório é um projeto `fpm` independente. Os programas contêm
verificações internas com `error stop`, de forma que uma tradução incorreta
também faz o exemplo falhar durante a execução.

| Exemplo | O que exercita |
|---|---|
| `01_scalars` | Letras gregas usadas como escalares |
| `02_indices` | Subscritos alfanuméricos, sobrescritos e sequências mistas |
| `03_literals` | Strings, `!` dentro de strings, aspas escapadas e comentários |
| `04_modules` | Projeto multifonte, módulo e argumentos Unicode |
| `05_statistics` | Arrays, função, tipo derivado e componentes Unicode |
| `06_oscillator` | Simulação numérica, `real64`, estado derivado e muitas iterações |

Depois de instalar o projeto em modo editável:

```bash
python3 -m pip install -e .
python3 examples/run_all.py
```

Para executar apenas um exemplo:

```bash
cd examples/04_modules
fpm uf90 run
```

O plugin cria os arquivos `*.f90` ao lado dos respectivos `*.f90u`. Eles são
artefatos gerados e estão ignorados pelo `.gitignore` desta pasta.

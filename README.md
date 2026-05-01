# Lab de Protecao de Dados com SQLite

Este laboratorio demonstra conceitos de protecao de dados em bancos de dados usando Python e SQLite:

- Data Redaction, ou mascaramento em tempo de exibicao.
- Anonimizacao irreversivel.
- Pseudo-anonimizacao reversivel apenas com uma tabela de mapeamento.
- Simulacao didatica de Transparent Data Encryption (TDE).

## Materiais do projeto

- [INSTRUCTIONS.md](./INSTRUCTIONS.md): roteiro de instalacao, execucao e uso interativo.
- [QUERIES.md](./QUERIES.md): queries prontas para praticar no SQLite.
- [EXERCISES.md](./EXERCISES.md): exercicios para alunos responderem durante a aula.
- [DIAGRAM.md](./DIAGRAM.md): diagrama do fluxo de protecao dos dados.

## Aviso importante sobre TDE

SQLite nao possui TDE nativo. Neste lab, a parte de TDE e uma simulacao educacional: os campos sensiveis sao criptografados pela aplicacao antes de serem gravados e descriptografados em runtime apenas por uma rotina autorizada.

Para reduzir troubleshooting em sala, a simulacao usa apenas bibliotecas padrao do Python. A cifra usada no exemplo serve para demonstrar o fluxo de dados cifrados em repouso; nao deve ser usada em producao.

Em producao, TDE real normalmente e fornecido pelo SGBD ou por uma extensao/produto especifico, com gestao de chaves, controle de acesso, auditoria e rotacao de chaves.

## Pre-requisitos

Para a execucao recomendada, instale:

- Docker Desktop, Docker Engine ou ambiente equivalente com suporte a `docker build` e `docker run`.
- Git, caso voce queira clonar este projeto a partir do GitHub.

Nao e necessario instalar Python, SQLite ou dependencias Python na maquina do aluno quando usar Docker.

## Instalar a partir do GitHub

Depois que este projeto estiver publicado no GitHub, use:

```bash
git clone <URL_DO_REPOSITORIO>
cd <PASTA_DO_REPOSITORIO>
```

Se voce recebeu os arquivos por outro meio, apenas entre na pasta onde estao `Dockerfile`, `README.md` e `src/`.

## Executar com Docker, modo automatico

Construa a imagem:

```bash
docker build -t lab-protecao-dados .
```

Execute o laboratorio completo:

```bash
docker run --rm lab-protecao-dados
```

Esse modo imprime todas as secoes no terminal: banco original, mascaramento, anonimizacao, pseudo-anonimizacao e TDE simulado.

Para executar apenas uma secao:

```bash
docker run --rm lab-protecao-dados python -m src.main --section redaction
docker run --rm lab-protecao-dados python -m src.main --section anonymization
docker run --rm lab-protecao-dados python -m src.main --section pseudonymization
docker run --rm lab-protecao-dados python -m src.main --section tde
```

## Executar com Docker, modo interativo

Use este modo para entrar no container, recriar o banco e testar queries manualmente com o cliente `sqlite3`:

```bash
docker run --rm -it lab-protecao-dados sh
```

Dentro do container, gere o banco e as tabelas de demonstracao:

```bash
python -m src.main
```

Depois abra o SQLite:

```bash
sqlite3 demo_protecao_dados.db
```

Exemplos de queries manuais:

```sql
.tables

SELECT id, nome_completo, cpf, email, salario
FROM funcionarios;

SELECT *
FROM vw_funcionarios_mascarados;

SELECT id, cpf_criptografado, salario_criptografado
FROM funcionarios_tde_simulado;

SELECT pseudonimo_id, email_dominio, faixa_salarial
FROM funcionarios_pseudo;
```

Para sair do SQLite:

```sql
.exit
```

Para sair do container:

```bash
exit
```

## Executar localmente, sem Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

Se o comando `python` nao existir no seu sistema, use `python3`.

O script recria o arquivo `demo_protecao_dados.db` a cada execucao para manter o lab previsivel.

Tambem e possivel executar apenas uma secao localmente:

```bash
python -m src.main --section redaction
python -m src.main --section anonymization
python -m src.main --section pseudonymization
python -m src.main --section tde
```

## Observacao sobre queries de TDE

No SQLite interativo, voce consegue consultar os dados cifrados armazenados na tabela `funcionarios_tde_simulado`. A descriptografia autorizada do TDE simulado acontece no Python, nao no motor SQLite. Por isso:

- query direta no SQLite mostra o campo cifrado;
- `python -m src.main` mostra a rotina autorizada descriptografando em runtime.

Veja [INSTRUCTIONS.md](./INSTRUCTIONS.md) para um roteiro de aula com comandos e queries sugeridas.

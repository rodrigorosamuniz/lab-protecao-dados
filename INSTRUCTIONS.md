# Instrucoes do Laboratorio

Este arquivo e um roteiro pratico para executar o lab e testar queries dentro do container Docker.

Materiais complementares:

- [QUERIES.md](./QUERIES.md): lista maior de queries prontas para pratica.
- [EXERCISES.md](./EXERCISES.md): exercicios para responder durante a aula.
- [DIAGRAM.md](./DIAGRAM.md): diagrama do fluxo de protecao.

## 1. Construir a imagem Docker

No diretorio do projeto, onde estao `Dockerfile`, `README.md` e `src/`, execute:

```bash
docker build -t lab-protecao-dados .
```

## 2. Rodar o laboratorio automatico

```bash
docker run --rm lab-protecao-dados
```

Esse comando executa o script completo e mostra:

- dados sensiveis em texto plano;
- mascaramento em tempo de exibicao;
- anonimizacao irreversivel;
- pseudo-anonimizacao com tabela de mapeamento;
- TDE simulado com dados cifrados e descriptografia em runtime.

Para executar apenas uma secao:

```bash
docker run --rm lab-protecao-dados python -m src.main --section baseline
docker run --rm lab-protecao-dados python -m src.main --section redaction
docker run --rm lab-protecao-dados python -m src.main --section anonymization
docker run --rm lab-protecao-dados python -m src.main --section pseudonymization
docker run --rm lab-protecao-dados python -m src.main --section tde
```

## 3. Entrar no container para testar queries manualmente

```bash
docker run --rm -it lab-protecao-dados sh
```

Dentro do container, primeiro rode o script para criar o banco e popular todas as tabelas:

```bash
python -m src.main
```

O banco criado se chama:

```text
demo_protecao_dados.db
```

Abra o cliente SQLite:

```bash
sqlite3 demo_protecao_dados.db
```

## 4. Ver tabelas disponiveis

Dentro do prompt do SQLite:

```sql
.tables
```

Tabelas principais:

- `funcionarios`: dados originais em texto plano.
- `vw_funcionarios_mascarados`: view que aplica mascaramento em SQL.
- `funcionarios_anonimizados`: dados anonimizados irreversivelmente.
- `funcionarios_pseudo`: dados pseudo-anonimizados.
- `mapa_pseudonimos`: tabela secreta de reversao dos pseudonimos.
- `funcionarios_plaintext`: copia em texto plano usada na comparacao com TDE.
- `funcionarios_tde_simulado`: dados cifrados para simular TDE.

O arquivo [QUERIES.md](./QUERIES.md) contem exemplos adicionais para cada uma dessas tabelas.

## 5. Query sem protecao

```sql
SELECT id, nome_completo, cpf, email, telefone, salario, data_nascimento
FROM funcionarios;
```

O resultado mostra dados sensiveis em texto plano. Esse e o cenario de risco usado como base para comparar as tecnicas.

## 6. Query de anonimizacao

```sql
SELECT pessoa_id, nome_generico, cpf, email, telefone,
       faixa_salarial, decada_nascimento
FROM funcionarios_anonimizados;
```

Essa tabela remove identificadores diretos e generaliza informacoes. Ela nao possui a relacao direta com a pessoa original.

## 7. Query de pseudo-anonimizacao

Tabela publica pseudo-anonimizada:

```sql
SELECT pseudonimo_id, email_dominio, faixa_salarial, ano_nascimento
FROM funcionarios_pseudo;
```

Tabela de mapeamento, que deve ser protegida em producao:

```sql
SELECT pseudonimo_id, funcionario_id, nome_completo, cpf, email, telefone
FROM mapa_pseudonimos;
```

Reidentificacao usando o mapa:

```sql
SELECT p.pseudonimo_id, m.nome_completo, m.cpf, p.faixa_salarial
FROM funcionarios_pseudo p
JOIN mapa_pseudonimos m ON m.pseudonimo_id = p.pseudonimo_id;
```

## 8. Query de TDE simulado, sem chave

```sql
SELECT id,
       nome_completo_criptografado,
       cpf_criptografado,
       email_criptografado,
       salario_criptografado
FROM funcionarios_tde_simulado;
```

Essa query mostra os dados cifrados armazenados no banco. No conceito de TDE, o objetivo e que dados em repouso nao fiquem legiveis diretamente no armazenamento.

## 9. TDE simulado, com rotina autorizada

A descriptografia autorizada nao acontece diretamente no SQLite deste lab. Ela acontece no Python:

```bash
python -m src.main
```

Na secao `TDE simulado`, o script mostra:

- query em texto plano sem TDE;
- query com dados cifrados;
- resultado descriptografado em runtime pela rotina autorizada.

## 10. Query de mascaramento

O mascaramento deste lab acontece em runtime no Python para deixar claro que Data Redaction nao altera o dado persistido.

Para ver o mascaramento:

```bash
python -m src.main
```

Na secao `Data Redaction`, compare:

- `Dados originais`;
- `Dados mascarados em runtime`.

No SQLite puro, a tabela `funcionarios` continua com os dados originais. Isso demonstra a diferenca entre proteger a exibicao e modificar o dado armazenado.

Tambem existe uma view para praticar mascaramento diretamente em SQL:

```sql
SELECT *
FROM vw_funcionarios_mascarados;
```

## 11. Sair do ambiente interativo

Para sair do SQLite:

```sql
.exit
```

Para sair do container:

```bash
exit
```

## 12. Limitacoes didaticas

- SQLite nao possui TDE nativo.
- A cifra usada no lab e apenas didatica e usa bibliotecas padrao do Python para evitar troubleshooting em sala.
- Em producao, use TDE real do SGBD ou criptografia robusta com gestao de chaves, KMS/HSM, rotacao, controle de acesso e auditoria.
- Pseudo-anonimizacao ainda e dado pessoal quando existe uma tabela de mapeamento.
- Mascaramento protege a visualizacao, mas nao remove o dado sensivel do banco.

## 13. Material de pratica

Use [QUERIES.md](./QUERIES.md) como folha de exercicios para os alunos. Ele inclui queries para:

- consultar dados originais sem protecao;
- aplicar mascaramento diretamente em SQL;
- analisar a tabela anonimizada;
- comparar pseudo-anonimizacao com e sem tabela de mapeamento;
- consultar dados cifrados do TDE simulado;
- entender por que a descriptografia autorizada acontece no Python neste lab.

Use [EXERCISES.md](./EXERCISES.md) para perguntas guiadas e [DIAGRAM.md](./DIAGRAM.md) para explicar o fluxo visualmente.

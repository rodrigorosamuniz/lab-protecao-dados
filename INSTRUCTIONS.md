# Instrucoes do Laboratório

Este arquivo e um roteiro pratico para executar o lab e testar queries dentro do container Docker.

Materiais complementares:

- [QUERIES.md](./QUERIES.md): lista maior de queries prontas para prática.
- [EXERCISES.md](./EXERCISES.md): exercícios para responder durante a aula.
- [DIAGRAM.md](./DIAGRAM.md): diagrama do fluxo de proteção.

## 1. Construir a imagem Docker

No diretório do projeto, onde estao `Dockerfile`, `README.md` e `src/`, execute:

```bash
docker build -t lab-protecao-dados .
```

## 2. Rodar o laboratório automatico

```bash
docker run --rm lab-protecao-dados
```

Esse comando executa o script completo e mostra:

- dados sensíveis em texto plano;
- mascaramento em tempo de exibicao;
- anonimização irreversível;
- pseudo-anonimização com tabela de mapeamento;
- TDE simulado com dados cifrados e descriptografia em runtime.

Para executar apenas uma seção:

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

## 4. Ver tabelas disponíveis

Dentro do prompt do SQLite:

```sql
.tables
```

Tabelas principaís:

- `funcionarios`: dados originais em texto plano.
- `vw_funcionarios_mascarados`: view que aplica mascaramento em SQL.
- `funcionarios_anonimizados`: dados anonimizados irreversívelmente.
- `funcionarios_pseudo`: dados pseudo-anonimizados.
- `mapa_pseudonimos`: tabela secreta de reversao dos pseudonimos.
- `funcionarios_plaintext`: copia em texto plano usada na comparação com TDE.
- `funcionarios_tde_simulado`: dados cifrados para simular TDE.

O arquivo [QUERIES.md](./QUERIES.md) contem exemplos adicionais para cada uma dessas tabelas.

## 5. Query sem proteção

```sql
SELECT id, nome_completo, cpf, email, telefone, salario, data_nascimento
FROM funcionarios;
```

O resultado mostra dados sensíveis em texto plano. Esse e o cenario de risco usado como base para comparar as técnicas.

## 6. Query de anonimização

```sql
SELECT pessoa_id, nome_generico, cpf, email, telefone,
       faixa_salarial, decada_nascimento
FROM funcionarios_anonimizados;
```

Essa tabela remove identificadores diretos e generaliza informações. Ela nao possui a relação direta com a pessoa original.

## 7. Query de pseudo-anonimização

Tabela publica pseudo-anonimizada:

```sql
SELECT pseudonimo_id, email_dominio, faixa_salarial, ano_nascimento
FROM funcionarios_pseudo;
```

Tabela de mapeamento, que deve ser protegida em produção:

```sql
SELECT pseudonimo_id, funcionario_id, nome_completo, cpf, email, telefone
FROM mapa_pseudonimos;
```

Reidentificação usando o mapa:

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

Na seção `TDE simulado`, o script mostra:

- query em texto plano sem TDE;
- query com dados cifrados;
- resultado descriptografado em runtime pela rotina autorizada.

## 10. Query de mascaramento

O mascaramento deste lab acontece em runtime no Python para deixar claro que Data Redaction nao altera o dado persistido.

Para ver o mascaramento:

```bash
python -m src.main
```

Na seção `Data Redaction`, compare:

- `Dados originais`;
- `Dados mascarados em runtime`.

No SQLite puro, a tabela `funcionarios` continua com os dados originais. Isso demonstra a diferenca entre proteger a exibicao e modificar o dado armazenado.

Tambem existe uma view para práticar mascaramento diretamente em SQL:

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

## 12. Limitações didáticas

- SQLite nao possui TDE nativo.
- A cifra usada no lab e apenas didática e usa bibliotecas padrao do Python para evitar troubleshooting em sala.
- Em produção, use TDE real do SGBD ou criptografia robusta com gestao de chaves, KMS/HSM, rotação, controle de acesso e auditoria.
- Pseudo-anonimização ainda e dado pessoal quando existe uma tabela de mapeamento.
- Mascaramento protege a visualização, mas nao remove o dado sensível do banco.

## 13. Material de prática

Use [QUERIES.md](./QUERIES.md) como folha de exercícios para os alunos. Ele inclui queries para:

- consultar dados originais sem proteção;
- aplicar mascaramento diretamente em SQL;
- analisar a tabela anonimizada;
- comparar pseudo-anonimização com e sem tabela de mapeamento;
- consultar dados cifrados do TDE simulado;
- entender por que a descriptografia autorizada acontece no Python neste lab.

Use [EXERCISES.md](./EXERCISES.md) para perguntas guiadas e [DIAGRAM.md](./DIAGRAM.md) para explicar o fluxo visualmente.

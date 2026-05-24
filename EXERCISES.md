# Exercícios do Laboratório

Use estes exercícios depois de executar o laboratório e abrir o banco no SQLite.

## Preparação

```bash
docker build -t lab-protecao-dados .
docker run --rm -it lab-protecao-dados sh
python -m src.main
sqlite3 demo_protecao_dados.db
```

No SQLite:

```sql
.headers on
.mode column
.tables
```

## Parte 1: Dados em texto plano

1. Execute uma query na tabela `funcionarios` mostrando `nome_completo`, `cpf`, `email` e `salario`.

2. Responda: quais colunas permitem identificar diretamente uma pessoa?

3. Ordene os funcionarios por `salario` do maior para o menor.

4. Responda: por que salário e data de nascimento tambem podem ser sensíveis mesmo quando nao sao identificadores únicos?

## Parte 2: Mascaramento

1. Consulte a view de mascaramento:

```sql
SELECT *
FROM vw_funcionarios_mascarados;
```

2. Compare a view com a tabela original:

```sql
SELECT
  f.id,
  f.cpf AS cpf_original,
  v.cpf_mascarado,
  f.email AS email_original,
  v.email_mascarado
FROM funcionarios f
JOIN vw_funcionarios_mascarados v ON v.id = f.id;
```

3. Responda: o mascaramento alterou os dados armazenados ou apenas a exibicao?

4. Cite um cenario em que mascaramento e melhor do que remover o dado.

## Parte 3: Anonimização

1. Consulte a tabela anonimizada:

```sql
SELECT *
FROM funcionarios_anonimizados;
```

2. Agrupe pessoas por decada de nascimento:

```sql
SELECT decada_nascimento, COUNT(*) AS quantidade
FROM funcionarios_anonimizados
GROUP BY decada_nascimento;
```

3. Responda: quais dados foram removidos ou generalizados?

4. Responda: por que essa técnica e adequada para compartilhar uma base em uma aula ou relatorio estatistico?

## Parte 4: Pseudo-anonimização

1. Consulte a tabela pseudo-anonimizada:

```sql
SELECT *
FROM funcionarios_pseudo;
```

2. Consulte a tabela de mapeamento:

```sql
SELECT *
FROM mapa_pseudonimos;
```

3. Reidentifique um registro:

```sql
SELECT
  p.pseudonimo_id,
  m.nome_completo,
  m.cpf,
  p.faixa_salarial
FROM funcionarios_pseudo p
JOIN mapa_pseudonimos m ON m.pseudonimo_id = p.pseudonimo_id
WHERE p.pseudonimo_id = 'ID_CRIPT_001';
```

4. Responda: por que pseudo-anonimização ainda deve ser tratada como dado pessoal?

5. Responda: que controles voce aplicaria sobre a tabela `mapa_pseudonimos` em produção?

## Parte 5: TDE simulado

1. Compare texto plano e texto cifrado:

```sql
SELECT
  p.id,
  p.cpf AS cpf_texto_plano,
  t.cpf_criptografado AS cpf_cifrado
FROM funcionarios_plaintext p
JOIN funcionarios_tde_simulado t ON t.id = p.id;
```

2. Consulte apenas a tabela cifrada:

```sql
SELECT id, cpf_criptografado, email_criptografado, salario_criptografado
FROM funcionarios_tde_simulado;
```

3. Saia do SQLite e rode apenas a seção de TDE:

```sql
.exit
```

```bash
python -m src.main --section tde
```

4. Responda: qual e a diferenca entre ver o dado cifrado no SQLite e ver o dado descriptografado pela rotina autorizada?

5. Responda: por que este laboratório chama essa parte de TDE simulado, e nao TDE real?

## Parte 6: Comparação final

Preencha a tabela:

| Técnica | Altera dado armazenado? | Permite reversao? | Uso indicado |
| --- | --- | --- | --- |
| Mascaramento |  |  |  |
| Anonimização |  |  |  |
| Pseudo-anonimização |  |  |  |
| TDE |  |  |  |

## Gabarito orientativo

- Mascaramento protege a visualização, mas a tabela original continua com dados completos.
- Anonimização remove ou generaliza identificadores e nao deve permitir reidentificação prática.
- Pseudo-anonimização substitui identificadores por códigos, mas pode ser revertida com o mapa.
- TDE protege dados em repouso; neste lab o conceito e simulado com criptografia de campo em Python porque SQLite nao possui TDE nativo.

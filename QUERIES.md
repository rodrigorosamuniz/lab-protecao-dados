# Queries para Praticar

Este arquivo traz exemplos de queries para os alunos executarem manualmente dentro do container.

## Preparar o ambiente

Entre no container:

```bash
docker run --rm -it lab-protecao-dados sh
```

Gere o banco e as tabelas do lab:

```bash
python -m src.main
```

Abra o SQLite:

```bash
sqlite3 demo_protecao_dados.db
```

Opcionalmente, melhore a exibicao no SQLite:

```sql
.headers on
.mode column
```

Liste as tabelas:

```sql
.tables
```

## 1. Dados originais sem protecao

Consulta completa da tabela original:

```sql
SELECT id, nome_completo, cpf, email, telefone, salario, data_nascimento
FROM funcionarios;
```

Consulta focada em identificadores diretos:

```sql
SELECT id, nome_completo, cpf, email
FROM funcionarios;
```

Consulta de dados financeiros em texto plano:

```sql
SELECT id, nome_completo, salario
FROM funcionarios
ORDER BY salario DESC;
```

## 2. Mascaramento com SQL

O mascaramento abaixo acontece apenas na saida da query. A tabela original continua armazenando os dados completos.

Consultar a view pronta de mascaramento:

```sql
SELECT *
FROM vw_funcionarios_mascarados;
```

Mascarar CPF, email e telefone:

```sql
SELECT
  id,
  nome_completo,
  '***.***.***-**' AS cpf_mascarado,
  substr(email, 1, 1) || '***@' || substr(email, instr(email, '@') + 1) AS email_mascarado,
  substr(telefone, 1, 4) || ' *****-' || substr(telefone, -4) AS telefone_mascarado
FROM funcionarios;
```

Mascarar salario por faixa e data de nascimento por ano:

```sql
SELECT
  id,
  nome_completo,
  CASE
    WHEN salario < 7000 THEN 'faixa: ate 7 mil'
    WHEN salario < 12000 THEN 'faixa: 7 a 12 mil'
    ELSE 'faixa: acima de 12 mil'
  END AS salario_mascarado,
  substr(data_nascimento, 1, 4) || '-**-**' AS nascimento_mascarado
FROM funcionarios;
```

Comparar dado original e dado mascarado lado a lado:

```sql
SELECT
  id,
  cpf AS cpf_original,
  '***.***.***-**' AS cpf_mascarado,
  email AS email_original,
  substr(email, 1, 1) || '***@' || substr(email, instr(email, '@') + 1) AS email_mascarado
FROM funcionarios;
```

## 3. Anonimizacao

Consultar a tabela anonimizada:

```sql
SELECT *
FROM funcionarios_anonimizados;
```

Agrupar por faixa salarial e decada de nascimento:

```sql
SELECT
  faixa_salarial,
  decada_nascimento,
  COUNT(*) AS quantidade
FROM funcionarios_anonimizados
GROUP BY faixa_salarial, decada_nascimento;
```

Contar pessoas por decada:

```sql
SELECT
  decada_nascimento,
  COUNT(*) AS pessoas
FROM funcionarios_anonimizados
GROUP BY decada_nascimento
ORDER BY decada_nascimento;
```

Mostrar que identificadores diretos foram removidos:

```sql
SELECT pessoa_id, nome_generico, cpf, email, telefone
FROM funcionarios_anonimizados;
```

## 4. Pseudo-anonimizacao

Consultar a tabela pseudo-anonimizada publica:

```sql
SELECT *
FROM funcionarios_pseudo;
```

Consultar apenas atributos analiticos:

```sql
SELECT
  pseudonimo_id,
  faixa_salarial,
  ano_nascimento
FROM funcionarios_pseudo
ORDER BY pseudonimo_id;
```

Agrupar por faixa salarial:

```sql
SELECT
  faixa_salarial,
  COUNT(*) AS quantidade
FROM funcionarios_pseudo
GROUP BY faixa_salarial;
```

Consultar a tabela de mapeamento secreta:

```sql
SELECT
  pseudonimo_id,
  funcionario_id,
  nome_completo,
  cpf,
  email,
  telefone
FROM mapa_pseudonimos;
```

Reidentificar pessoas usando o mapa:

```sql
SELECT
  p.pseudonimo_id,
  p.faixa_salarial,
  p.ano_nascimento,
  m.nome_completo,
  m.cpf
FROM funcionarios_pseudo p
JOIN mapa_pseudonimos m
  ON m.pseudonimo_id = p.pseudonimo_id;
```

Demonstrar que o pseudonimo sozinho nao mostra nome ou CPF:

```sql
SELECT
  pseudonimo_id,
  email_dominio,
  faixa_salarial
FROM funcionarios_pseudo
WHERE pseudonimo_id = 'ID_CRIPT_001';
```

Demonstrar reversao com acesso ao mapa:

```sql
SELECT
  p.pseudonimo_id,
  m.nome_completo,
  m.cpf,
  m.email
FROM funcionarios_pseudo p
JOIN mapa_pseudonimos m
  ON m.pseudonimo_id = p.pseudonimo_id
WHERE p.pseudonimo_id = 'ID_CRIPT_001';
```

## 5. TDE simulado

Comparar tabela sem TDE com tabela cifrada:

```sql
SELECT id, nome_completo, cpf, email, salario
FROM funcionarios_plaintext;
```

Consultar dados cifrados no banco:

```sql
SELECT
  id,
  cpf_criptografado,
  salario_criptografado
FROM funcionarios_tde_simulado;
```

Ver tamanho dos valores cifrados:

```sql
SELECT
  id,
  length(cpf_criptografado) AS tamanho_cpf_cifrado,
  length(email_criptografado) AS tamanho_email_cifrado,
  length(salario_criptografado) AS tamanho_salario_cifrado
FROM funcionarios_tde_simulado;
```

Comparar texto plano e texto cifrado lado a lado:

```sql
SELECT
  p.id,
  p.cpf AS cpf_texto_plano,
  t.cpf_criptografado AS cpf_cifrado
FROM funcionarios_plaintext p
JOIN funcionarios_tde_simulado t
  ON t.id = p.id;
```

Comparar email em texto plano e cifrado:

```sql
SELECT
  p.id,
  p.email AS email_texto_plano,
  t.email_criptografado AS email_cifrado
FROM funcionarios_plaintext p
JOIN funcionarios_tde_simulado t
  ON t.id = p.id;
```

## 6. Descriptografia autorizada

No lab, a descriptografia autorizada do TDE simulado acontece no Python, nao diretamente no SQLite.

Saia do SQLite:

```sql
.exit
```

Rode novamente:

```bash
python -m src.main
```

Na secao `TDE simulado`, compare:

- `SEM TDE`: dados em texto plano;
- `COM TDE simulado, sem chave/autorizacao`: dados cifrados;
- `COM TDE simulado, com rotina autorizada`: dados descriptografados em runtime.

## 7. Encerrar

Para sair do SQLite:

```sql
.exit
```

Para sair do container:

```bash
exit
```

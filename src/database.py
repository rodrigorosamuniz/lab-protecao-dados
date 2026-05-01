from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

DB_PATH = Path("demo_protecao_dados.db")

FUNCIONARIOS = [
    {
        "nome_completo": "Ana Carolina Souza",
        "cpf": "123.456.789-01",
        "email": "ana.souza@example.com",
        "telefone": "(11) 98888-1111",
        "salario": 8450.75,
        "data_nascimento": "1988-04-12",
    },
    {
        "nome_completo": "Bruno Henrique Lima",
        "cpf": "234.567.890-12",
        "email": "bruno.lima@example.com",
        "telefone": "(21) 97777-2222",
        "salario": 11200.00,
        "data_nascimento": "1992-09-30",
    },
    {
        "nome_completo": "Camila Ribeiro Alves",
        "cpf": "345.678.901-23",
        "email": "camila.alves@example.com",
        "telefone": "(31) 96666-3333",
        "salario": 6200.50,
        "data_nascimento": "1985-01-24",
    },
    {
        "nome_completo": "Diego Martins Rocha",
        "cpf": "456.789.012-34",
        "email": "diego.rocha@example.com",
        "telefone": "(41) 95555-4444",
        "salario": 15400.25,
        "data_nascimento": "1979-12-02",
    },
    {
        "nome_completo": "Elisa Fernanda Costa",
        "cpf": "567.890.123-45",
        "email": "elisa.costa@example.com",
        "telefone": "(51) 94444-5555",
        "salario": 7300.00,
        "data_nascimento": "1996-06-18",
    },
]


def connect() -> sqlite3.Connection:
    """Abre uma conexao SQLite configurada para retornar linhas nomeadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset_database() -> sqlite3.Connection:
    """Recria o banco para que a demonstracao seja sempre repetivel."""
    try:
        DB_PATH.unlink()
    except FileNotFoundError:
        pass

    conn = connect()
    conn.execute(
        """
        CREATE TABLE funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            cpf TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            salario REAL NOT NULL,
            data_nascimento TEXT NOT NULL
        )
        """
    )
    conn.executemany(
        """
        INSERT INTO funcionarios (
            nome_completo, cpf, email, telefone, salario, data_nascimento
        )
        VALUES (
            :nome_completo, :cpf, :email, :telefone, :salario, :data_nascimento
        )
        """,
        FUNCIONARIOS,
    )
    create_redaction_view(conn)
    conn.commit()
    return conn


def create_redaction_view(conn: sqlite3.Connection) -> None:
    """Cria uma view de mascaramento para consultas SQL manuais."""
    conn.execute("DROP VIEW IF EXISTS vw_funcionarios_mascarados")
    conn.execute(
        """
        CREATE VIEW vw_funcionarios_mascarados AS
        SELECT
            id,
            nome_completo,
            '***.***.***-**' AS cpf_mascarado,
            substr(email, 1, 1) || '***@' || substr(email, instr(email, '@') + 1) AS email_mascarado,
            substr(telefone, 1, 4) || ' *****-' || substr(telefone, -4) AS telefone_mascarado,
            CASE
                WHEN salario < 7000 THEN 'faixa: ate 7 mil'
                WHEN salario < 12000 THEN 'faixa: 7 a 12 mil'
                ELSE 'faixa: acima de 12 mil'
            END AS salario_mascarado,
            substr(data_nascimento, 1, 4) || '-**-**' AS nascimento_mascarado
        FROM funcionarios
        """
    )


def fetch_all(conn: sqlite3.Connection, sql: str, params: Iterable[object] = ()) -> list[dict]:
    """Executa uma consulta SELECT e devolve dicionarios para facilitar exibicao."""
    cursor = conn.execute(sql, tuple(params))
    return [dict(row) for row in cursor.fetchall()]

from __future__ import annotations

import sqlite3

from .database import fetch_all
from .display import explain, print_table, show_sql, subsection


def salary_band(salary: float) -> str:
    if salary < 7000:
        return "ate 7 mil"
    if salary < 12000:
        return "7 a 12 mil"
    return "acima de 12 mil"


def birth_decade(date_text: str) -> str:
    year = int(date_text[:4])
    decade = year - (year % 10)
    return f"decada de {decade}"


def create_anonymized_table(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS funcionarios_anonimizados")
    conn.execute(
        """
        CREATE TABLE funcionarios_anonimizados (
            pessoa_id TEXT PRIMARY KEY,
            nome_generico TEXT NOT NULL,
            cpf TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            faixa_salarial TEXT NOT NULL,
            decada_nascimento TEXT NOT NULL
        )
        """
    )

    rows = fetch_all(
        conn,
        """
        SELECT id, salario, data_nascimento
        FROM funcionarios
        ORDER BY id;
        """,
    )
    anon_rows = [
        {
            "pessoa_id": f"ANON_{row['id']:03d}",
            "nome_generico": f"Pessoa{row['id']}",
            "cpf": "REMOVIDO",
            "email": "removido@example.invalid",
            "telefone": "REMOVIDO",
            "faixa_salarial": salary_band(float(row["salario"])),
            "decada_nascimento": birth_decade(row["data_nascimento"]),
        }
        for row in rows
    ]
    conn.executemany(
        """
        INSERT INTO funcionarios_anonimizados (
            pessoa_id, nome_generico, cpf, email, telefone,
            faixa_salarial, decada_nascimento
        )
        VALUES (
            :pessoa_id, :nome_generico, :cpf, :email, :telefone,
            :faixa_salarial, :decada_nascimento
        )
        """,
        anon_rows,
    )
    conn.commit()


def run_demo(conn: sqlite3.Connection) -> None:
    subsection("2. Anonimizacao: substituicao irreversivel")
    explain(
        """
        Anonimizacao remove ou generaliza identificadores para que o titular
        nao possa ser reconstruido a partir da tabela resultante. E adequada
        para analises estatisticas, aulas e compartilhamento de bases quando
        nao ha necessidade de reidentificar pessoas.
        """
    )
    create_anonymized_table(conn)

    original_sql = """
    SELECT id, nome_completo, cpf, email, telefone, salario, data_nascimento
    FROM funcionarios
    ORDER BY id;
    """
    anonymized_sql = """
    SELECT pessoa_id, nome_generico, cpf, email, telefone,
           faixa_salarial, decada_nascimento
    FROM funcionarios_anonimizados
    ORDER BY pessoa_id;
    """
    show_sql(original_sql)
    print("Dados originais:")
    print_table(fetch_all(conn, original_sql))
    show_sql(anonymized_sql)
    print("Dados anonimizados permanentemente na nova tabela:")
    print_table(fetch_all(conn, anonymized_sql))

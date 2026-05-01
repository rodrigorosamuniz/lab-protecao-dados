from __future__ import annotations

import sqlite3

from .database import fetch_all
from .display import explain, print_table, show_sql, subsection


def create_pseudonymized_tables(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS funcionarios_pseudo")
    conn.execute("DROP TABLE IF EXISTS mapa_pseudonimos")
    conn.execute(
        """
        CREATE TABLE funcionarios_pseudo (
            pseudonimo_id TEXT PRIMARY KEY,
            email_dominio TEXT NOT NULL,
            faixa_salarial TEXT NOT NULL,
            ano_nascimento TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE mapa_pseudonimos (
            pseudonimo_id TEXT PRIMARY KEY,
            funcionario_id INTEGER NOT NULL,
            nome_completo TEXT NOT NULL,
            cpf TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL
        )
        """
    )

    rows = fetch_all(
        conn,
        """
        SELECT id, nome_completo, cpf, email, telefone, salario, data_nascimento
        FROM funcionarios
        ORDER BY id;
        """,
    )
    public_rows = []
    mapping_rows = []
    for index, row in enumerate(rows, start=1):
        pseudonym = f"ID_CRIPT_{index:03d}"
        domain = row["email"].split("@", maxsplit=1)[1]
        public_rows.append(
            {
                "pseudonimo_id": pseudonym,
                "email_dominio": domain,
                "faixa_salarial": _salary_band(float(row["salario"])),
                "ano_nascimento": row["data_nascimento"][:4],
            }
        )
        mapping_rows.append(
            {
                "pseudonimo_id": pseudonym,
                "funcionario_id": row["id"],
                "nome_completo": row["nome_completo"],
                "cpf": row["cpf"],
                "email": row["email"],
                "telefone": row["telefone"],
            }
        )

    conn.executemany(
        """
        INSERT INTO funcionarios_pseudo (
            pseudonimo_id, email_dominio, faixa_salarial, ano_nascimento
        )
        VALUES (
            :pseudonimo_id, :email_dominio, :faixa_salarial, :ano_nascimento
        )
        """,
        public_rows,
    )
    conn.executemany(
        """
        INSERT INTO mapa_pseudonimos (
            pseudonimo_id, funcionario_id, nome_completo, cpf, email, telefone
        )
        VALUES (
            :pseudonimo_id, :funcionario_id, :nome_completo, :cpf, :email, :telefone
        )
        """,
        mapping_rows,
    )
    conn.commit()


def run_demo(conn: sqlite3.Connection) -> None:
    subsection("3. Pseudo-anonimizacao: reversivel com tabela de mapeamento")
    explain(
        """
        Pseudo-anonimizacao troca identificadores diretos por codigos. Ela
        reduz exposicao em tabelas operacionais ou analiticas, mas continua
        sendo dado pessoal se a tabela de mapeamento existir. Em producao,
        separe e proteja o mapa com controles fortes.
        """
    )
    create_pseudonymized_tables(conn)

    public_sql = """
    SELECT pseudonimo_id, email_dominio, faixa_salarial, ano_nascimento
    FROM funcionarios_pseudo
    ORDER BY pseudonimo_id;
    """
    mapping_sql = """
    SELECT pseudonimo_id, funcionario_id, nome_completo, cpf, email, telefone
    FROM mapa_pseudonimos
    ORDER BY pseudonimo_id;
    """
    join_sql = """
    SELECT p.pseudonimo_id, m.nome_completo, m.cpf, p.faixa_salarial
    FROM funcionarios_pseudo p
    JOIN mapa_pseudonimos m ON m.pseudonimo_id = p.pseudonimo_id
    ORDER BY p.pseudonimo_id;
    """

    show_sql(public_sql)
    print("Tabela pseudo-anonimizada visivel para analise:")
    print_table(fetch_all(conn, public_sql))
    show_sql(mapping_sql)
    print("Tabela de mapeamento secreta, que permite reversao:")
    print_table(fetch_all(conn, mapping_sql))
    show_sql(join_sql)
    print("Reidentificacao possivel apenas com acesso ao mapa:")
    print_table(fetch_all(conn, join_sql))


def _salary_band(salary: float) -> str:
    if salary < 7000:
        return "ate 7 mil"
    if salary < 12000:
        return "7 a 12 mil"
    return "acima de 12 mil"

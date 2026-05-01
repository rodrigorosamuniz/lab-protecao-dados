from __future__ import annotations

import sqlite3

from .database import fetch_all
from .display import explain, print_table, show_sql, subsection


def mask_cpf(cpf: str) -> str:
    return "***.***.***-**"


def mask_email(email: str) -> str:
    usuario, dominio = email.split("@", maxsplit=1)
    inicial = usuario[:1]
    return f"{inicial}***@{dominio}"


def mask_phone(phone: str) -> str:
    return phone[:4] + " *****-" + phone[-4:]


def mask_salary(salary: float) -> str:
    if salary < 7000:
        return "faixa: ate 7 mil"
    if salary < 12000:
        return "faixa: 7 a 12 mil"
    return "faixa: acima de 12 mil"


def mask_birth_date(date_text: str) -> str:
    year = date_text[:4]
    return f"{year}-**-**"


def redact_row(row: dict) -> dict:
    return {
        "id": row["id"],
        "nome_completo": row["nome_completo"],
        "cpf": mask_cpf(row["cpf"]),
        "email": mask_email(row["email"]),
        "telefone": mask_phone(row["telefone"]),
        "salario": mask_salary(float(row["salario"])),
        "data_nascimento": mask_birth_date(row["data_nascimento"]),
    }


def run_demo(conn: sqlite3.Connection) -> None:
    subsection("1. Data Redaction: mascaramento em tempo de exibicao")
    explain(
        """
        Redaction protege a exibicao sem alterar o dado original no banco.
        E util quando um atendente, relatorio ou tela precisa ver apenas parte
        do dado. Em producao, combine com controle de acesso e auditoria.
        """
    )

    sql = """
    SELECT id, nome_completo, cpf, email, telefone, salario, data_nascimento
    FROM funcionarios
    ORDER BY id;
    """
    rows = fetch_all(conn, sql)
    redacted = [redact_row(row) for row in rows]

    show_sql(sql)
    print("Dados originais:")
    print_table(rows)
    print("Dados mascarados em runtime:")
    print_table(redacted)

    view_sql = """
    SELECT id, nome_completo, cpf_mascarado, email_mascarado,
           telefone_mascarado, salario_mascarado, nascimento_mascarado
    FROM vw_funcionarios_mascarados
    ORDER BY id;
    """
    show_sql(view_sql)
    print("View SQLite de mascaramento para consultas manuais:")
    print_table(fetch_all(conn, view_sql))

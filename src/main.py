from __future__ import annotations

import argparse
from collections.abc import Callable

from . import anonymization, pseudonymization, redaction, tde_simulation
from .database import fetch_all, reset_database
from .display import explain, print_table, section, show_sql, subsection


def main() -> None:
    args = parse_args()

    section("Laboratorio de protecao de dados em bancos")
    explain(
        """
        Este script cria um banco SQLite ficticio e demonstra tecnicas comuns
        de protecao de dados. Todos os dados sao inventados para fins didaticos.

        Importante: SQLite nao possui Transparent Data Encryption nativo.
        A secao de TDE deste lab simula o conceito com criptografia de campos
        feita pela aplicacao, para que seja possivel observar queries com dados
        em texto plano, dados cifrados e descriptografia em runtime.
        """
    )

    conn = reset_database()
    try:
        run_sections(conn, args.section)
    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Laboratorio educacional de protecao de dados com SQLite."
    )
    parser.add_argument(
        "--section",
        choices=["all", "baseline", "redaction", "anonymization", "pseudonymization", "tde"],
        default="all",
        help="Executa apenas uma secao especifica do laboratorio.",
    )
    return parser.parse_args()


def run_sections(conn, selected: str) -> None:
    demos: dict[str, Callable] = {
        "baseline": show_plaintext_baseline,
        "redaction": redaction.run_demo,
        "anonymization": anonymization.run_demo,
        "pseudonymization": pseudonymization.run_demo,
        "tde": tde_simulation.run_demo,
    }

    if selected == "all":
        for demo in demos.values():
            demo(conn)
        show_summary()
        return

    demos[selected](conn)


def show_summary() -> None:
    section("Resumo final")
    explain(
        """
        Mascaramento altera apenas a exibicao. Anonimizacao remove a
        possibilidade pratica de reidentificacao. Pseudo-anonimizacao reduz
        exposicao, mas ainda permite reversao com o mapa. TDE protege dados
        em repouso; neste SQLite a protecao foi simulada em nivel de campo.
        """
    )


def show_plaintext_baseline(conn) -> None:
    subsection("Banco simulado: dados sensiveis em texto plano")
    explain(
        """
        Primeiro, veja a situacao sem protecao: uma consulta comum retorna CPF,
        email, telefone, salario e data de nascimento diretamente do banco.
        Este e o risco basico que as tecnicas seguintes ajudam a reduzir.
        """
    )
    sql = """
    SELECT id, nome_completo, cpf, email, telefone, salario, data_nascimento
    FROM funcionarios
    ORDER BY id;
    """
    show_sql(sql)
    print_table(fetch_all(conn, sql))


if __name__ == "__main__":
    main()

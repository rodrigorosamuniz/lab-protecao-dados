from __future__ import annotations

import base64
import hashlib
import sqlite3

from .database import fetch_all
from .display import explain, print_table, show_sql, subsection


DEMO_SECRET = "chave-didatica-nao-usar-em-producao"


def encrypt_text(value: object) -> str:
    """Cifra reversivel didatica, apenas para demonstrar o fluxo de TDE.

    Em producao, use criptografia autenticada de biblioteca consolidada,
    chaves fora do codigo, KMS/HSM, rotacao e controle de acesso.
    """
    plaintext = str(value).encode("utf-8")
    ciphertext = _xor_with_keystream(plaintext)
    return base64.urlsafe_b64encode(ciphertext).decode("ascii")


def decrypt_text(token: str) -> str:
    ciphertext = base64.urlsafe_b64decode(token.encode("ascii"))
    plaintext = _xor_with_keystream(ciphertext)
    return plaintext.decode("utf-8")


def _xor_with_keystream(data: bytes) -> bytes:
    key = hashlib.sha256(DEMO_SECRET.encode("utf-8")).digest()
    output = bytearray()
    counter = 0
    while len(output) < len(data):
        counter_bytes = counter.to_bytes(4, "big")
        output.extend(hashlib.sha256(key + counter_bytes).digest())
        counter += 1
    return bytes(byte ^ mask for byte, mask in zip(data, output))


def create_tde_tables(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS funcionarios_plaintext")
    conn.execute("DROP TABLE IF EXISTS funcionarios_tde_simulado")
    conn.execute(
        """
        CREATE TABLE funcionarios_plaintext AS
        SELECT id, nome_completo, cpf, email, telefone, salario, data_nascimento
        FROM funcionarios
        """
    )
    conn.execute(
        """
        CREATE TABLE funcionarios_tde_simulado (
            id INTEGER PRIMARY KEY,
            nome_completo_criptografado TEXT NOT NULL,
            cpf_criptografado TEXT NOT NULL,
            email_criptografado TEXT NOT NULL,
            telefone_criptografado TEXT NOT NULL,
            salario_criptografado TEXT NOT NULL,
            data_nascimento_criptografada TEXT NOT NULL
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
    encrypted_rows = [
        {
            "id": row["id"],
            "nome_completo_criptografado": encrypt_text(row["nome_completo"]),
            "cpf_criptografado": encrypt_text(row["cpf"]),
            "email_criptografado": encrypt_text(row["email"]),
            "telefone_criptografado": encrypt_text(row["telefone"]),
            "salario_criptografado": encrypt_text(row["salario"]),
            "data_nascimento_criptografada": encrypt_text(row["data_nascimento"]),
        }
        for row in rows
    ]
    conn.executemany(
        """
        INSERT INTO funcionarios_tde_simulado (
            id,
            nome_completo_criptografado,
            cpf_criptografado,
            email_criptografado,
            telefone_criptografado,
            salario_criptografado,
            data_nascimento_criptografada
        )
        VALUES (
            :id,
            :nome_completo_criptografado,
            :cpf_criptografado,
            :email_criptografado,
            :telefone_criptografado,
            :salario_criptografado,
            :data_nascimento_criptografada
        )
        """,
        encrypted_rows,
    )
    conn.commit()


def authorized_decrypt_rows(rows: list[dict]) -> list[dict]:
    decrypted = []
    for row in rows:
        decrypted.append(
            {
                "id": row["id"],
                "nome_completo": decrypt_text(row["nome_completo_criptografado"]),
                "cpf": decrypt_text(row["cpf_criptografado"]),
                "email": decrypt_text(row["email_criptografado"]),
                "telefone": decrypt_text(row["telefone_criptografado"]),
                "salario": decrypt_text(row["salario_criptografado"]),
                "data_nascimento": decrypt_text(row["data_nascimento_criptografada"]),
            }
        )
    return decrypted


def run_demo(conn: sqlite3.Connection) -> None:
    subsection("4. TDE simulado: dados cifrados em repouso")
    explain(
        """
        SQLite nao possui TDE nativo. Esta secao simula o conceito criptografando
        campos sensiveis antes da gravacao. A query sem chave ve texto cifrado;
        a rotina autorizada descriptografa em runtime. Em TDE real, essa
        transparencia costuma ser fornecida pelo SGBD e pela gestao de chaves.
        A cifra desta aula usa apenas biblioteca padrao para evitar dependencias
        no container; ela e didatica e nao deve ser usada em producao.
        """
    )
    create_tde_tables(conn)

    plain_sql = """
    SELECT id, nome_completo, cpf, email, telefone, salario, data_nascimento
    FROM funcionarios_plaintext
    ORDER BY id;
    """
    encrypted_sql = """
    SELECT id,
           nome_completo_criptografado,
           cpf_criptografado,
           email_criptografado,
           telefone_criptografado,
           salario_criptografado,
           data_nascimento_criptografada
    FROM funcionarios_tde_simulado
    ORDER BY id;
    """

    show_sql(plain_sql)
    print("SEM TDE: dados sensiveis armazenados e consultados em texto plano:")
    print_table(fetch_all(conn, plain_sql))

    encrypted_rows = fetch_all(conn, encrypted_sql)
    show_sql(encrypted_sql)
    print("COM TDE simulado, sem chave/autorizacao: o banco retorna texto cifrado:")
    print_table(encrypted_rows)

    print("COM TDE simulado, com rotina autorizada: descriptografia em runtime:")
    print_table(authorized_decrypt_rows(encrypted_rows))

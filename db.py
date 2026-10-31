from pathlib import Path
import sqlite3

PASTA_PROJETO = Path(__file__).resolve().parent

PASTA_INSTANCE = PASTA_PROJETO / "instance"
CAMINHO_BANCO = PASTA_INSTANCE / "leaftrial.db"


def criar_banco():
    PASTA_INSTANCE.mkdir(exist_ok=True)

    with sqlite3.connect(CAMINHO_BANCO) as conexao:

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                valor INTEGER NOT NULL,
                descricao TEXT
            )
        """)
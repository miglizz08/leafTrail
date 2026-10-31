from pathlib import Path
import sqlite3

PASTA_PROJETO = Path(__file__).resolve().parent

PASTA_INSTANCE = PASTA_PROJETO / "instance"
CAMINHO_BANCO = PASTA_INSTANCE / "leaftrial.db"
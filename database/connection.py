import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


class DatabaseConfigurationError(RuntimeError):
    """Raised when required database environment variables are missing or invalid."""


def get_connection():
    """Abre uma conexão com o MySQL usando variáveis de ambiente."""
    required_settings = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
    missing_settings = [name for name in required_settings if not os.getenv(name)]

    if missing_settings:
        missing = ", ".join(missing_settings)
        raise DatabaseConfigurationError(f"Configuração do banco ausente: {missing}")

    try:
        port = int(os.getenv("DB_PORT", "3306"))
    except ValueError as error:
        raise DatabaseConfigurationError("DB_PORT deve ser um número inteiro.") from error

    connection_settings = {
        "host": os.environ["DB_HOST"],
        "port": port,
        "database": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "use_pure": True,
    }

    ssl_ca = os.getenv("DB_SSL_CA")
    if ssl_ca:
        connection_settings.update(
            ssl_ca=ssl_ca,
            ssl_verify_cert=True,
            ssl_verify_identity=True,
        )

    return mysql.connector.connect(**connection_settings)

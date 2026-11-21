import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import mysql.connector
from flask import Flask, abort, redirect, render_template, request, url_for

from database.connection import DatabaseConfigurationError, get_connection


app = Flask(__name__)

CATEGORIES = {
    "alimentacao",
    "transporte",
    "lazer",
    "contas_assinaturas",
    "outros",
}
CATEGORY_LABELS = {
    "alimentacao": "Alimentação",
    "transporte": "Transporte",
    "lazer": "Lazer",
    "contas_assinaturas": "Contas & Assinaturas",
    "outros": "Outros",
}


@app.template_filter("brl")
def format_brl(value):
    whole, cents = f"{value:.2f}".split(".")
    whole_with_separators = f"{int(whole):,}".replace(",", ".")
    return f"R$ {whole_with_separators},{cents}"


@app.template_filter("expense_date")
def format_expense_date(value):
    month_names = ("Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez")
    return f"{value.day:02d} {month_names[value.month - 1]} {value.year}"


def validate_expense(form):
    description = form.get("descricao", "").strip()
    raw_amount = form.get("valor", "").strip()
    category = form.get("categoria", "")
    raw_date = form.get("data", "")

    if not description:
        raise ValueError("Informe uma descrição para o gasto.")

    if len(description) > 255:
        raise ValueError("A descrição deve ter no máximo 255 caracteres.")

    if not category or category not in CATEGORIES:
        raise ValueError("Selecione uma categoria válida.")

    try:
        expense_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError("Informe uma data válida.") from error

    if "," in raw_amount:
        valid_amount = re.fullmatch(r"(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d{0,2})?", raw_amount)
        normalized_amount = raw_amount.replace(".", "").replace(",", ".")
    else:
        valid_amount = re.fullmatch(r"\d+(?:\.\d{1,2})?", raw_amount)
        normalized_amount = raw_amount

    if not valid_amount:
        raise ValueError("Informe um valor válido, com até duas casas decimais.")

    try:
        amount = Decimal(normalized_amount).quantize(Decimal("0.01"))
    except InvalidOperation as error:
        raise ValueError("Informe um valor válido.") from error

    if amount <= 0:
        raise ValueError("O valor deve ser maior que zero.")

    if amount > Decimal("99999999.99"):
        raise ValueError("O valor excede o limite permitido.")

    return expense_date, amount, category, description or None


def render_expense_form(error=None, status=200, *, is_edit=False, expense_id=None):
    return (
        render_template(
            "novo_gasto.html",
            today=date.today().isoformat(),
            form_data=request.form,
            error=error,
            is_edit=is_edit,
            expense_id=expense_id,
        ),
        status,
    )


@app.route("/")
def dashboard():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, descricao, categoria, data, valor
            FROM gastos
            ORDER BY data DESC, id DESC
            """
        )
        expenses = cursor.fetchall()

        cursor.execute("SELECT COALESCE(SUM(valor), 0) AS total FROM gastos")
        total = cursor.fetchone()["total"]

    except (mysql.connector.Error, DatabaseConfigurationError):
        app.logger.exception("Não foi possível carregar os gastos do banco de dados.")
        return render_template("dashboard.html", db_error=True), 503
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    return render_template(
        "dashboard.html",
        expenses=expenses,
        category_labels=CATEGORY_LABELS,
        total=total,
    )


@app.route("/novo-gasto", methods=["GET", "POST"])
def novo_gasto():
    if request.method == "GET":
        return render_template(
            "novo_gasto.html",
            today=date.today().isoformat(),
            success=request.args.get("salvo") == "1",
        )

    try:
        expense_date, amount, category, description = validate_expense(request.form)
    except ValueError as error:
        return render_expense_form(str(error), status=400)

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO gastos (data, valor, categoria, descricao)
            VALUES (%s, %s, %s, %s)
            """,
            (expense_date, amount, category, description),
        )
        connection.commit()
    except (mysql.connector.Error, DatabaseConfigurationError):
        if connection is not None:
            connection.rollback()
        app.logger.exception("Não foi possível salvar o gasto no banco de dados.")
        return render_expense_form(
            "Banco de dados indisponível neste ambiente. Confira a configuração e tente novamente.",
            status=503,
        )
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    return redirect(url_for("novo_gasto", salvo=1))


@app.route("/gastos/<int:expense_id>/editar", methods=["GET", "POST"])
def editar_gasto(expense_id):
    connection = None
    cursor = None

    if request.method == "GET":
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, descricao, categoria, data, valor FROM gastos WHERE id = %s",
                (expense_id,),
            )
            expense = cursor.fetchone()
        except (mysql.connector.Error, DatabaseConfigurationError):
            app.logger.exception("Não foi possível carregar o gasto para edição.")
            return "Não foi possível carregar o gasto.", 503
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

        if expense is None:
            abort(404)

        expense["data"] = expense["data"].isoformat()
        return render_template(
            "novo_gasto.html",
            today=date.today().isoformat(),
            form_data=expense,
            is_edit=True,
            expense_id=expense_id,
        )

    try:
        expense_date, amount, category, description = validate_expense(request.form)
    except ValueError as error:
        return render_expense_form(
            str(error),
            status=400,
            is_edit=True,
            expense_id=expense_id,
        )

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id FROM gastos WHERE id = %s",
            (expense_id,),
        )
        if cursor.fetchone() is None:
            abort(404)

        cursor.execute(
            """
            UPDATE gastos
            SET data = %s, valor = %s, categoria = %s, descricao = %s
            WHERE id = %s
            """,
            (expense_date, amount, category, description, expense_id),
        )
        connection.commit()
    except (mysql.connector.Error, DatabaseConfigurationError):
        if connection is not None:
            connection.rollback()
        app.logger.exception("Não foi possível atualizar o gasto no banco de dados.")
        return render_expense_form(
            "Banco de dados indisponível neste ambiente. Confira a configuração e tente novamente.",
            status=503,
            is_edit=True,
            expense_id=expense_id,
        )
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    return redirect(url_for("dashboard"))


@app.route("/gastos/<int:expense_id>/excluir", methods=["POST"])
def excluir_gasto(expense_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM gastos WHERE id = %s", (expense_id,))

        if cursor.rowcount == 0:
            abort(404)

        connection.commit()
    except (mysql.connector.Error, DatabaseConfigurationError):
        if connection is not None:
            connection.rollback()
        app.logger.exception("Não foi possível excluir o gasto do banco de dados.")
        return "Não foi possível excluir o gasto. Tente novamente.", 503
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)

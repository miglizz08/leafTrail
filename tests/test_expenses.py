from datetime import date
from decimal import Decimal

import pytest

import app as app_module
from app import validate_expense


def expense_form(**overrides):
    values = {
        "descricao": "Compras do mês",
        "valor": "123,45",
        "categoria": "alimentacao",
        "data": "2026-11-15",
    }
    values.update(overrides)
    return values


def test_validate_expense_parses_brazilian_currency():
    parsed = validate_expense(expense_form(valor="1.234,56"))

    assert parsed == (
        date(2026, 11, 15),
        Decimal("1234.56"),
        "alimentacao",
        "Compras do mês",
    )


def test_validate_expense_rejects_empty_description():
    with pytest.raises(ValueError, match="descrição"):
        validate_expense(expense_form(descricao="   "))


@pytest.mark.parametrize("value", ["0", "-10,00", "abc", "10,999"])
def test_validate_expense_rejects_invalid_amount(value):
    with pytest.raises(ValueError):
        validate_expense(expense_form(valor=value))


def test_validate_expense_rejects_unknown_category():
    with pytest.raises(ValueError, match="categoria"):
        validate_expense(expense_form(categoria="nao_existe"))


def test_validate_expense_rejects_invalid_date():
    with pytest.raises(ValueError, match="data"):
        validate_expense(expense_form(data="2026-02-30"))


def test_validate_expense_rejects_description_over_255_characters():
    with pytest.raises(ValueError, match="255"):
        validate_expense(expense_form(descricao="x" * 256))


class FakeCursor:
    def __init__(self, expenses, total):
        self.expenses = expenses
        self.total = total
        self.result = None

    def execute(self, query):
        self.result = "total" if "SUM(valor)" in query else "expenses"

    def fetchall(self):
        return self.expenses

    def fetchone(self):
        return {"total": self.total, "expense_count": len(self.expenses)}

    def close(self):
        pass


class FakeConnection:
    def __init__(self, expenses, total):
        self.cursor_instance = FakeCursor(expenses, total)

    def cursor(self, dictionary=False):
        return self.cursor_instance

    def is_connected(self):
        return True

    def close(self):
        pass


@pytest.mark.parametrize(
    ("expenses", "total", "expected_total"),
    [
        ([{"id": 1, "descricao": "Compra", "categoria": "alimentacao", "data": date(2026, 11, 15), "valor": Decimal("23.50")}], Decimal("23.50"), "R$ 23,50"),
        ([], Decimal("0.00"), "R$ 0,00"),
    ],
)
def test_dashboard_displays_database_total(monkeypatch, expenses, total, expected_total):
    monkeypatch.setattr(
        app_module,
        "get_connection",
        lambda: FakeConnection(expenses, total),
    )
    app_module.app.config["TESTING"] = True

    response = app_module.app.test_client().get("/")

    assert response.status_code == 200
    assert expected_total.encode() in response.data
    expected_count = len(expenses)
    expected_label = "lançamento" if expected_count == 1 else "lançamentos"
    assert f"{expected_count} {expected_label}".encode() in response.data

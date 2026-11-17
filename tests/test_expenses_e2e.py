from datetime import date
from decimal import Decimal
from threading import Thread

import pytest
from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

import app as app_module


class MemoryStore:
    def __init__(self):
        self.expenses = []
        self.next_id = 1

    def connect(self):
        return MemoryConnection(self)


class MemoryConnection:
    def __init__(self, store):
        self.store = store

    def cursor(self, dictionary=False):
        return MemoryCursor(self.store, dictionary)

    def is_connected(self):
        return True

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class MemoryCursor:
    def __init__(self, store, dictionary):
        self.store = store
        self.dictionary = dictionary
        self.rows = []
        self.rowcount = 0

    def execute(self, query, params=None):
        query = " ".join(query.split()).upper()
        params = params or ()

        if query.startswith("INSERT INTO GASTOS"):
            expense_date, amount, category, description = params
            self.store.expenses.append({
                "id": self.store.next_id,
                "data": expense_date,
                "valor": amount,
                "categoria": category,
                "descricao": description,
            })
            self.store.next_id += 1
        elif query.startswith("SELECT COALESCE(SUM(VALOR)"):
            self.rows = [{"total": sum(
                (expense["valor"] for expense in self.store.expenses),
                Decimal("0.00"),
            )}]
        elif query.startswith("SELECT") and "FROM GASTOS WHERE ID = %S" in query:
            expense = next(
                (item for item in self.store.expenses if item["id"] == params[0]),
                None,
            )
            if expense is None:
                self.rows = []
            elif self.dictionary:
                self.rows = [expense.copy()]
            else:
                self.rows = [(expense["id"],)]
        elif query.startswith("SELECT") and "FROM GASTOS" in query:
            ordered = sorted(
                self.store.expenses,
                key=lambda item: (item["data"], item["id"]),
                reverse=True,
            )
            self.rows = [item.copy() for item in ordered]
        elif query.startswith("UPDATE GASTOS"):
            expense_date, amount, category, description, expense_id = params
            expense = next(
                (item for item in self.store.expenses if item["id"] == expense_id),
                None,
            )
            if expense is not None:
                expense.update(data=expense_date, valor=amount,
                               categoria=category, descricao=description)
        elif query.startswith("DELETE FROM GASTOS"):
            expense_id = params[0]
            before = len(self.store.expenses)
            self.store.expenses[:] = [
                item for item in self.store.expenses if item["id"] != expense_id
            ]
            self.rowcount = before - len(self.store.expenses)
        else:
            raise AssertionError(f"Consulta não implementada no banco de teste: {query}")

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows

    def close(self):
        pass


@pytest.fixture
def live_app(monkeypatch, request):
    store = MemoryStore()
    monkeypatch.setattr(app_module, "get_connection", store.connect)
    app_module.app.config["TESTING"] = True

    server = make_server("127.0.0.1", 0, app_module.app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_user_can_create_edit_and_delete_expense(live_app):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(f"{live_app}/novo-gasto")
            page.locator("#descricao").fill("Almoço de teste")
            page.locator("#valor").fill("35,50")
            page.locator("#categoria").select_option("alimentacao")
            page.locator("#data").fill(date.today().isoformat())
            page.get_by_role("button", name="Salvar Gasto").click()
            expect(page.get_by_role("status")).to_have_text("Gasto salvo com sucesso.")

            page.goto(live_app)
            expect(page.get_by_role("heading", name="Meus Gastos")).to_be_visible()
            expect(page.get_by_text("Almoço de teste")).to_be_visible()
            expect(page.get_by_text("R$ 35,50").first).to_be_visible()

            page.get_by_role("link", name="Editar gasto").click()
            expect(page.get_by_role("heading", name="Editar Gasto")).to_be_visible()
            page.locator("#descricao").fill("Almoço atualizado")
            page.locator("#valor").fill("42,00")
            page.get_by_role("button", name="Atualizar Gasto").click()
            expect(page.get_by_text("Almoço atualizado")).to_be_visible()
            expect(page.get_by_role("cell", name="R$ 42,00")).to_be_visible()

            page.on("dialog", lambda dialog: dialog.accept())
            page.get_by_role("button", name="Excluir gasto").click()
            expect(page.get_by_text("Nenhum gasto cadastrado ainda.")).to_be_visible()
            expect(page.get_by_text("R$ 0,00")).to_be_visible()
        finally:
            browser.close()

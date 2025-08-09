import pytest
from rich.table import Table
from rich.console import Console

from MyTable import MyTable


@pytest.fixture
def data():
    columns = ["ID", "Name"]
    rows = [
        ["1", "Alice"],
        ["2", "Bob"],
        ["3", "Charlie"],
    ]
    row_styles = {1: "red", 2: "green"}  # стили для строк 1 и 2
    return columns, rows, row_styles


def test_show_adds_columns_and_rows_with_row_styles(monkeypatch, data):
    columns, rows, row_styles = data
    calls_add_column = []
    calls_add_row = []

    def fake_add_column(self, *args, **kwargs):
        print(self.__class__.__name__)
        calls_add_column.append((args, kwargs))

    def fake_add_row(self, *args, **kwargs):
        print(self.__class__.__name__)
        calls_add_row.append((args, kwargs))

    # Спаи на методы Table
    monkeypatch.setattr(Table, "add_column", fake_add_column, raising=True)
    monkeypatch.setattr(Table, "add_row", fake_add_row, raising=True)

    tbl = MyTable()
    # не обязательно, pytest и так перехватывает stdout
    tbl.console = Console()

    tbl.show("Users", columns, rows, row_styles=row_styles)

    # Проверяем, что колонки добавлены по именам (без стилевых kwargs)
    assert [c[0][0] for c in calls_add_column] == columns
    assert all(c[1] == {} for c in calls_add_column)

    # Проверяем строки и стили
    assert len(calls_add_row) == len(rows)

    # row 0 — стиль пустая строка
    assert calls_add_row[0][0] == tuple(rows[0])
    assert calls_add_row[0][1].get("style") == ""
    # row 1 — "red"
    assert calls_add_row[1][0] == tuple(rows[1])
    assert calls_add_row[1][1].get("style") == "red"
    # row 2 — "green"
    assert calls_add_row[2][0] == tuple(rows[2])
    assert calls_add_row[2][1].get("style") == "green"


def test_show_prints_table(monkeypatch, data):
    columns, rows, row_styles = data

    printed = {"called": False, "arg_type": None}

    def fake_console_print(self, obj, *args, **kwargs):
        printed["called"] = True
        printed["arg_type"] = type(obj)

    tbl = MyTable()
    # Патчим print только на инстансе Console
    monkeypatch.setattr(type(tbl.console), "print",
                        fake_console_print, raising=True)

    tbl.show("Users", columns, rows, row_styles=row_styles)

    assert printed["called"] is True
    # Убедимся, что выводится именно Table
    assert printed["arg_type"] is Table

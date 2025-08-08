import builtins
import pytest

import Menu as menu_mod


# ----------------- helpers -----------------

def _patch_inputs(monkeypatch, values):
    """Feed successive input() values to code under test."""
    it = iter(values)

    def _fake_input(_prompt=""):
        print(f"Fake input: {_prompt.strip()}")
        try:
            return next(it)
        except StopIteration:
            raise AssertionError(
                "Input sequence exhausted; add more test inputs")

    monkeypatch.setattr(builtins, "input", _fake_input, raising=True)


# Фейковая таблица, чтобы перехватывать вызов .show(...)
class _FakeTable:
    last_calls: list[dict] = []

    def show(self, title, columns, rows, row_styles=None):
        _FakeTable.last_calls.append(
            {"title": title, "columns": columns,
                "rows": rows, "row_styles": row_styles}
        )


@pytest.fixture(autouse=True)
def patch_mytable(monkeypatch):
    # Подменяем MyTable внутри Menu.py на наш фейк
    monkeypatch.setattr(menu_mod, "MyTable", _FakeTable, raising=True)
    # Чистим историю вызовов перед каждым тестом
    _FakeTable.last_calls.clear()
    # Сбрасываем rows_count
    menu_mod.Menu.rows_count = 0
    yield


# ----------------- tests: display -----------------

def test_display_calls_mytable_show_and_sets_rows_count():
    title = "Main"
    cols = ["Index", "Name"]
    rows = [["0", "Alpha"], ["1", "Beta"]]
    styles = {0: "bold"}

    menu_mod.Menu.display(title, cols, rows, row_styles=styles)

    # проверяем rows_count
    assert menu_mod.Menu.rows_count == len(rows)

    # проверяем вызов MyTable.show
    assert len(_FakeTable.last_calls) == 1
    call = _FakeTable.last_calls[0]
    assert call["title"] == title
    assert call["columns"] == cols
    assert call["rows"] == rows
    assert call["row_styles"] == styles


def test_display_sets_default_row_styles_when_none():
    title = "T"
    cols = ["A"]
    rows = [["0"]]

    menu_mod.Menu.display(title, cols, rows)  # row_styles=None

    call = _FakeTable.last_calls[0]
    # Внутри display, если None — создаётся {}
    assert call["row_styles"] == {}


# ----------------- tests: choose_option -----------------

def test_choose_option_accepts_valid_first_try(monkeypatch):
    # сначала подготовим rows_count через display
    menu_mod.Menu.display("T", ["C"], [["0"], ["1"], ["2"]])
    assert menu_mod.Menu.rows_count == 3

    _patch_inputs(monkeypatch, ["1"])

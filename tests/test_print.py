import pytest
from rich.console import Console
from io import StringIO

import Print as print_module           # <— модуль
from Print import Print                # <— класс


@pytest.fixture
def capture_rich_output():
    stream = StringIO()
    # markup=False — Rich не парсит [blue]/[green]/[red], теги останутся в тексте
    console = Console(file=stream, force_terminal=False, markup=False)
    return stream, console


def test_info_output(monkeypatch, capture_rich_output):
    stream, console = capture_rich_output
    monkeypatch.setattr(print_module, "print", console.print)  # <— патчим имя в модуле
    Print.info("Test Info")
    out = stream.getvalue()
    assert "[blue]Test Info" in out
    assert "=" * 20 in out


def test_success_output(monkeypatch, capture_rich_output):
    stream, console = capture_rich_output
    monkeypatch.setattr(print_module, "print", console.print)
    Print.success("Test Success")
    out = stream.getvalue()
    assert "[green]Test Success" in out
    assert "=" * 20 in out


def test_error_output(monkeypatch, capture_rich_output):
    stream, console = capture_rich_output
    monkeypatch.setattr(print_module, "print", console.print)
    Print.error("Test Error")
    out = stream.getvalue()
    assert "[red]Test Error" in out
    assert "=" * 20 in out

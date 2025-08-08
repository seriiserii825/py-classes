import os
from pathlib import Path
from typing_extensions import ClassVar, List, Optional
import pytest

from FilesHandle import FilesHandle


class _SelectMock:
    # Will be reassigned per-test
    _next_select_one_return: ClassVar[Optional[str]] = None
    _next_select_with_fzf_return: ClassVar[Optional[List[str]]] = None

    @staticmethod
    def select_one(options):
        _SelectMock.last_options = options
        return _SelectMock._next_select_one_return

    @staticmethod
    def select_with_fzf(options):
        _SelectMock.last_options = options
        return _SelectMock._next_select_with_fzf_return


class _InputValidatorMock:
    # Will be reassigned per-test
    _next_string = "newdir"

    @staticmethod
    def get_string(prompt: str) -> str:
        print(f"InputValidatorMock: {prompt}")
        return _InputValidatorMock._next_string


class _PrintMock:
    last_error = None

    @staticmethod
    def error(msg: str):
        _PrintMock.last_error = msg


class _TerminalMenuMock:
    def __init__(self, options, **kwargs):
        self.options = options
        self.kwargs = kwargs
        # Will be reassigned per-test
        self.chosen_menu_entries = []

    def show(self):
        # Nothing interactive in tests
        return None


@pytest.fixture(autouse=True)
def isolate_cwd(tmp_path, monkeypatch):
    """Run each test in an isolated temp directory and patch noisy bits."""
    monkeypatch.chdir(tmp_path)

    # Patch external dependencies imported by FilesHandle module
    import FilesHandle as fh_mod  # type: ignore

    monkeypatch.setattr(fh_mod, "Select", _SelectMock, raising=True)
    monkeypatch.setattr(fh_mod, "InputValidator",
                        _InputValidatorMock, raising=True)
    monkeypatch.setattr(fh_mod, "Print", _PrintMock, raising=True)
    monkeypatch.setattr(fh_mod, "TerminalMenu",
                        _TerminalMenuMock, raising=True)

    # Silence os.system calls (e.g. "bat")
    calls = []
    monkeypatch.setattr(
        os, "system", lambda cmd: calls.append(cmd) or 0, raising=True)
    yield


# ---- Tests: list_files / list_dir ------------------------------------------

def test_list_files_no_filter(tmp_path, capsys):
    (tmp_path / "a.txt").write_text("A")
    (tmp_path / "b.py").write_text("B")
    fh = FilesHandle()
    fh.list_files(tmp_path)

    out = capsys.readouterr().out
    assert "Listing files in" in out
    assert "a.txt" in out and "b.py" in out


def test_list_files_with_extension(tmp_path, capsys):
    (tmp_path / "a.txt").write_text("A")
    (tmp_path / "b.py").write_text("B")
    fh = FilesHandle()
    fh.list_files(tmp_path, file_extension=".py")

    out = capsys.readouterr().out
    assert "b.py" in out and "a.txt" not in out


def test_list_dir_sorted(tmp_path, capsys):
    (tmp_path / "bbb").mkdir()
    (tmp_path / "aaa").mkdir()
    fh = FilesHandle()
    fh.list_dir(tmp_path)

    out = capsys.readouterr().out
    # Should be sorted alphabetically
    assert out.index("aaa") < out.index("bbb")


# ---- Tests: create_or_choose_directory / helpers ---------------------------

def test_create_or_choose_directory_when_no_dirs_creates(tmp_path):
    fh = FilesHandle()
    _InputValidatorMock._next_string = "newdir"

    result = fh.create_or_choose_directory(tmp_path)
    assert Path(result).is_dir()
    assert Path(result).name == "newdir"


def test_create_or_choose_directory_choose_create_branch(tmp_path):
    # Prepare one existing dir so _has_dirs returns True
    (tmp_path / "alpha").mkdir()
    fh = FilesHandle()

    _SelectMock._next_select_one_return = "Create"
    _InputValidatorMock._next_string = "beta"

    result = fh.create_or_choose_directory(tmp_path)
    assert Path(result).is_dir()
    assert Path(result).name == "beta"


def test_create_or_choose_directory_choose_existing_branch(tmp_path, monkeypatch):
    (tmp_path / "alpha").mkdir()
    (tmp_path / "beta").mkdir()

    # choose_dir returns a list like ["beta"]
    def fake_choose_dir(path):
        print(f"Choosing dir in {path}")
        return ["beta"]

    fh = FilesHandle()
    monkeypatch.setattr(fh, "choose_dir", fake_choose_dir)

    _SelectMock._next_select_one_return = "Select"

    result = fh.create_or_choose_directory(tmp_path)
    assert Path(result).name == "beta"


def test_choose_dir_uses_fzf_and_sorts(tmp_path):
    (tmp_path / "zeta").mkdir()
    (tmp_path / "alpha").mkdir()
    fh = FilesHandle()

    _SelectMock._next_select_with_fzf_return = ["alpha"]
    selected = fh.choose_dir(tmp_path)
    assert selected == ["alpha"]


def test_has_dirs_true_and_false(tmp_path):
    fh = FilesHandle()
    assert fh._has_dirs(tmp_path) is False
    (tmp_path / "sub").mkdir()
    assert fh._has_dirs(tmp_path) is True


# ---- Tests: choose_file -----------------------------------------------------

def test_choose_file_with_extension_filters_and_returns_selection(tmp_path):
    (tmp_path / "a.txt").write_text("A")
    (tmp_path / "b.py").write_text("B")
    fh = FilesHandle()

    _SelectMock._next_select_one_return = "b.py"
    chosen = fh.choose_file(tmp_path, extension=".py")
    assert chosen == "b.py"


def test_choose_file_no_files_exits_and_prints_error(tmp_path):
    fh = FilesHandle()
    with pytest.raises(SystemExit):
        fh.choose_file(tmp_path)
    assert _PrintMock.last_error == "No files found"


# ---- Tests: append_to_file --------------------------------------------------

def test_append_to_file_appends_and_calls_bat(tmp_path, monkeypatch):
    f = tmp_path / "file.txt"
    f.write_text("hello")
    fh = FilesHandle()

    os_system_calls = []

    def fake_system(cmd):
        os_system_calls.append(cmd)
        return 0

    monkeypatch.setattr(os, "system", fake_system, raising=True)

    fh.append_to_file(f, " world")
    assert f.read_text() == "hello world"
    assert os_system_calls == [f"bat {f}"]


# ---- Tests: select_multiple -------------------------------------------------

def test_select_multiple_uses_terminal_menu(monkeypatch):
    fh = FilesHandle()

    # We want TerminalMenu.show() to do nothing, and .chosen_menu_entries to be returned
    chosen = ["one", "three"]

    def fake_tm_ctor(options, **kwargs):
        tm = _TerminalMenuMock(options, **kwargs)
        tm.chosen_menu_entries = chosen
        return tm

    import FilesHandle as fh_mod  # type: ignore
    monkeypatch.setattr(fh_mod, "TerminalMenu", fake_tm_ctor, raising=True)

    result = fh.select_multiple(["one", "two", "three"])
    assert result == chosen

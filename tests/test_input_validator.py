import builtins

from InputValidator import InputValidator


def _patch_inputs(monkeypatch, values):
    """Feed successive inputs() values safely."""
    it = iter(values)

    def _fake_input(_prompt=""):
        print(f"Input prompt: {_prompt}", end="")
        try:
            return next(it)
        except StopIteration:
            raise AssertionError("Input sequence exhausted; add more test inputs")

    monkeypatch.setattr(builtins, "input", _fake_input)


# ------------------ get_int ------------------

def test_get_int_accepts_valid(monkeypatch):
    _patch_inputs(monkeypatch, ["42"])
    assert InputValidator.get_int("Enter: ") == 42


def test_get_int_reprompts_on_invalid_then_ok(monkeypatch, capsys):
    _patch_inputs(monkeypatch, ["nope", "10"])
    assert InputValidator.get_int("Enter: ") == 10
    out = capsys.readouterr().out
    assert "Invalid input. Please enter a valid integer." in out


# ------------------ get_float ------------------

def test_get_float_accepts_valid(monkeypatch):
    _patch_inputs(monkeypatch, ["3.14"])
    assert InputValidator.get_float("Enter: ") == 3.14


def test_get_float_reprompts_on_invalid_then_ok(monkeypatch, capsys):
    _patch_inputs(monkeypatch, ["x", "2.5"])
    assert InputValidator.get_float("Enter: ") == 2.5
    out = capsys.readouterr().out
    assert "Invalid input. Please enter a valid number." in out


# ------------------ get_string ------------------

def test_get_string_returns_trimmed_nonempty(monkeypatch):
    _patch_inputs(monkeypatch, ["  hello  "])
    assert InputValidator.get_string("Enter: ") == "hello"


def test_get_string_reprompts_on_empty_then_ok(monkeypatch, capsys):
    _patch_inputs(monkeypatch, ["", "  world "])
    assert InputValidator.get_string("Enter: ") == "world"
    out = capsys.readouterr().out
    assert "Input cannot be empty. Try again." in out


def test_get_string_allows_empty_when_flag_true(monkeypatch):
    _patch_inputs(monkeypatch, [""])
    assert InputValidator.get_string("Enter: ", allow_empty=True) == ""


# ------------------ _pretty_print ------------------

def test_pretty_print_outputs_value(capsys):
    iv = InputValidator()
    iv._pretty_print("abc")
    out = capsys.readouterr().out
    # We don't assert on ANSI color codes; just the important content
    assert "Value: abc" in out

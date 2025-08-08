import sys
import os

from PathHelper import PathHelper


def test_path_helper_initialization(monkeypatch, tmp_path):
    fake_script = tmp_path / "fake_main.py"
    fake_script.write_text("# dummy script")

    # Patch sys.argv[0] to point to fake script
    monkeypatch.setattr(sys, "argv", [str(fake_script)], raising=False)

    # Patch os.getcwd() to a controlled directory
    fake_cwd = tmp_path / "working_dir"
    fake_cwd.mkdir()
    monkeypatch.setattr(os, "getcwd", lambda: str(fake_cwd), raising=True)

    helper = PathHelper()

    # entry_point should resolve to our fake script path
    assert helper.get_entry_point == fake_script.resolve()

    # entry_dir should be the directory containing the fake script
    assert helper.get_entry_dir == fake_script.parent.resolve()

    # cwd should be the patched working directory
    assert helper.get_cwd == fake_cwd.resolve()


def test_get_cwd_property_reflects_current_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    helper = PathHelper()
    assert helper.get_cwd == tmp_path.resolve()

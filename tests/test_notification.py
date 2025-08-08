import os

from Notification import Notification


def test_notify_calls_os_system_with_correct_command(monkeypatch):
    calls = []

    def fake_system(cmd):
        calls.append(cmd)
        return 0  # pretend success

    monkeypatch.setattr(os, "system", fake_system, raising=True)

    notif = Notification("Test Title", "Test Message")
    notif.notify()

    assert len(calls) == 1
    expected_cmd = 'notify-send "Test Title" "Test Message"'
    assert calls[0] == expected_cmd


def test_notify_handles_special_characters(monkeypatch):
    calls = []
    monkeypatch.setattr(
        os, "system", lambda cmd: calls.append(cmd) or 0, raising=True)

    notif = Notification("Hello; rm -rf /", "This is > test")
    notif.notify()

    # No escaping is done in the class — the test documents current behavior
    assert 'Hello; rm -rf /' in calls[0]
    assert 'This is > test' in calls[0]

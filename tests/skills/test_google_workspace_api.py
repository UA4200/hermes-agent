"""Tests for Google Workspace gws bridge and CLI wrapper."""

import importlib.util
import json
import os
import subprocess
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


BRIDGE_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills/productivity/google-workspace/scripts/gws_bridge.py"
)
API_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills/productivity/google-workspace/scripts/google_api.py"
)


@pytest.fixture
def bridge_module(monkeypatch, tmp_path):
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))

    spec = importlib.util.spec_from_file_location("gws_bridge_test", BRIDGE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def api_module(monkeypatch, tmp_path):
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))

    spec = importlib.util.spec_from_file_location("gws_api_test", API_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    # Ensure the gws CLI code path is taken even when the binary isn't
    # installed (CI).  Without this, calendar_list() falls through to the
    # Python SDK path which imports ``googleapiclient`` — not in deps.
    module._gws_binary = lambda: "/usr/bin/gws"
    # Bypass authentication check — no real token file in CI.
    module._ensure_authenticated = lambda: None
    return module


def _write_token(path: Path, *, token="ya29.test", expiry=None, **extra):
    data = {
        "token": token,
        "refresh_token": "1//refresh",
        "client_id": "123.apps.googleusercontent.com",
        "client_secret": "secret",
        "token_uri": "https://oauth2.googleapis.com/token",
        **extra,
    }
    if expiry is not None:
        data["expiry"] = expiry
    path.write_text(json.dumps(data))


def test_bridge_returns_valid_token(bridge_module, tmp_path):
    """Non-expired token is returned without refresh."""
    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    token_path = bridge_module.get_token_path()
    _write_token(token_path, token="ya29.valid", expiry=future)

    result = bridge_module.get_valid_token()
    assert result == "ya29.valid"


def test_bridge_refreshes_expired_token(bridge_module, tmp_path):
    """Expired token triggers a refresh via token_uri."""
    past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    token_path = bridge_module.get_token_path()
    _write_token(token_path, token="ya29.old", expiry=past)

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({
        "access_token": "ya29.refreshed",
        "expires_in": 3600,
    }).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = bridge_module.get_valid_token()

    assert result == "ya29.refreshed"
    # Verify persisted
    saved = json.loads(token_path.read_text())
    assert saved["token"] == "ya29.refreshed"
    assert saved["type"] == "authorized_user"


def test_bridge_exits_on_missing_token(bridge_module):
    """Missing token file causes exit with code 1."""
    with pytest.raises(SystemExit):
        bridge_module.get_valid_token()


def test_bridge_main_injects_token_env(bridge_module, tmp_path):
    """main() sets GOOGLE_WORKSPACE_CLI_TOKEN in subprocess env."""
    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    token_path = bridge_module.get_token_path()
    _write_token(token_path, token="ya29.injected", expiry=future)

    captured = {}

    def capture_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["env"] = kwargs.get("env", {})
        return MagicMock(returncode=0)

    with patch.object(sys, "argv", ["gws_bridge.py", "gmail", "+triage"]):
        with patch.object(subprocess, "run", side_effect=capture_run):
            with pytest.raises(SystemExit):
                bridge_module.main()

    assert captured["env"]["GOOGLE_WORKSPACE_CLI_TOKEN"] == "ya29.injected"
    assert captured["cmd"] == ["gws", "gmail", "+triage"]


def test_api_calendar_list_uses_events_list(api_module):
    """calendar_list calls _run_gws with events list + params."""
    captured = {}

    def capture_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return MagicMock(returncode=0, stdout="{}", stderr="")

    args = api_module.argparse.Namespace(
        start="", end="", max=25, calendar="primary", func=api_module.calendar_list,
    )

    with patch.object(api_module.subprocess, "run", side_effect=capture_run):
        api_module.calendar_list(args)

    cmd = captured["cmd"]
    # _gws_binary() returns "/usr/bin/gws", so cmd[0] is that binary
    assert cmd[0] == "/usr/bin/gws"
    assert "calendar" in cmd
    assert "events" in cmd
    assert "list" in cmd
    assert "--params" in cmd
    params = json.loads(cmd[cmd.index("--params") + 1])
    assert "timeMin" in params
    assert "timeMax" in params
    assert params["calendarId"] == "primary"


def test_api_calendar_list_respects_date_range(api_module):
    """calendar list with --start/--end passes correct time bounds."""
    captured = {}

    def capture_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return MagicMock(returncode=0, stdout="{}", stderr="")

    args = api_module.argparse.Namespace(
        start="2026-04-01T00:00:00Z",
        end="2026-04-07T23:59:59Z",
        max=25,
        calendar="primary",
        func=api_module.calendar_list,
    )

    with patch.object(api_module.subprocess, "run", side_effect=capture_run):
        api_module.calendar_list(args)

    cmd = captured["cmd"]
    params_idx = cmd.index("--params")
    params = json.loads(cmd[params_idx + 1])
    assert params["timeMin"] == "2026-04-01T00:00:00Z"
    assert params["timeMax"] == "2026-04-07T23:59:59Z"


def test_api_get_credentials_refresh_persists_authorized_user_type(api_module, monkeypatch):
    token_path = api_module.TOKEN_PATH
    _write_token(token_path, token="ya29.old")

    class FakeCredentials:
        def __init__(self):
            self.expired = True
            self.refresh_token = "1//refresh"
            self.valid = True

        def refresh(self, request):
            self.expired = False

        def to_json(self):
            return json.dumps({
                "token": "ya29.refreshed",
                "refresh_token": "1//refresh",
                "client_id": "123.apps.googleusercontent.com",
                "client_secret": "secret",
                "token_uri": "https://oauth2.googleapis.com/token",
            })

    class FakeCredentialsModule:
        @staticmethod
        def from_authorized_user_file(filename, scopes):
            assert filename == str(token_path)
            assert scopes == api_module.SCOPES
            return FakeCredentials()

    google_module = types.ModuleType("google")
    oauth2_module = types.ModuleType("google.oauth2")
    credentials_module = types.ModuleType("google.oauth2.credentials")
    credentials_module.Credentials = FakeCredentialsModule
    transport_module = types.ModuleType("google.auth.transport")
    requests_module = types.ModuleType("google.auth.transport.requests")
    requests_module.Request = lambda: object()

    monkeypatch.setitem(sys.modules, "google", google_module)
    monkeypatch.setitem(sys.modules, "google.oauth2", oauth2_module)
    monkeypatch.setitem(sys.modules, "google.oauth2.credentials", credentials_module)
    monkeypatch.setitem(sys.modules, "google.auth.transport", transport_module)
    monkeypatch.setitem(sys.modules, "google.auth.transport.requests", requests_module)

    creds = api_module.get_credentials()

    saved = json.loads(token_path.read_text())
    assert isinstance(creds, FakeCredentials)
    assert saved["token"] == "ya29.refreshed"
    assert saved["type"] == "authorized_user"


# ---------------------------------------------------------------------------
# calendar summarize
# ---------------------------------------------------------------------------

def _fake_gws_events(events_json):
    """Return a subprocess.run mock that yields a gws calendar events list."""
    def _run(cmd, **kwargs):
        return MagicMock(returncode=0, stdout=json.dumps({"items": events_json}), stderr="")
    return _run


SAMPLE_EVENTS = [
    {
        "id": "evt1",
        "summary": "Daily Approval Window",
        "start": {"dateTime": "2026-07-21T09:00:00-05:00"},
        "end": {"dateTime": "2026-07-21T09:30:00-05:00"},
        "location": "",
        "description": "",
        "status": "confirmed",
        "htmlLink": "https://calendar.google.com/event?eid=evt1",
    },
    {
        "id": "evt2",
        "summary": "Evening Review",
        "start": {"dateTime": "2026-07-21T21:00:00-05:00"},
        "end": {"dateTime": "2026-07-21T21:20:00-05:00"},
        "location": "",
        "description": "",
        "status": "confirmed",
        "htmlLink": "https://calendar.google.com/event?eid=evt2",
    },
    {
        "id": "evt3",
        "summary": "Weekly Strategy Review",
        "start": {"dateTime": "2026-07-26T10:00:00-05:00"},
        "end": {"dateTime": "2026-07-26T11:00:00-05:00"},
        "location": "Home Office",
        "description": "Review empire metrics and plan next week.",
        "status": "confirmed",
        "htmlLink": "https://calendar.google.com/event?eid=evt3",
    },
]


def test_calendar_summarize_json_groups_by_day(api_module, capsys):
    """summarize --format json groups events into day buckets."""
    args = api_module.argparse.Namespace(
        week=False, days=7, calendar="primary", format="json",
        func=api_module.calendar_summarize,
    )

    with patch.object(api_module.subprocess, "run", side_effect=_fake_gws_events(SAMPLE_EVENTS)):
        api_module.calendar_summarize(args)

    out = json.loads(capsys.readouterr().out)
    assert out["total_events"] == 3
    assert len(out["days"]) == 2

    # Day 1: two events on 2026-07-21
    day1 = out["days"][0]
    assert day1["date"] == "2026-07-21"
    assert len(day1["events"]) == 2
    assert day1["events"][0]["summary"] == "Daily Approval Window"
    assert day1["events"][0]["time"] == "09:00"
    assert day1["events"][0]["end"] == "09:30"

    # Day 2: one event on 2026-07-26
    day2 = out["days"][1]
    assert day2["date"] == "2026-07-26"
    assert day2["events"][0]["location"] == "Home Office"


def test_calendar_summarize_markdown_output(api_module, capsys):
    """summarize --format markdown produces human-readable text."""
    args = api_module.argparse.Namespace(
        week=False, days=7, calendar="primary", format="markdown",
        func=api_module.calendar_summarize,
    )

    with patch.object(api_module.subprocess, "run", side_effect=_fake_gws_events(SAMPLE_EVENTS)):
        api_module.calendar_summarize(args)

    out = capsys.readouterr().out
    assert "## Calendar" in out
    assert "Daily Approval Window" in out
    assert "Weekly Strategy Review" in out
    assert "09:00" in out
    assert "Home Office" in out
    assert "3 events" in out


def test_calendar_summarize_empty_calendar(api_module, capsys):
    """summarize with no events returns zero totals and no day buckets."""
    args = api_module.argparse.Namespace(
        week=False, days=7, calendar="primary", format="json",
        func=api_module.calendar_summarize,
    )

    with patch.object(api_module.subprocess, "run", side_effect=_fake_gws_events([])):
        api_module.calendar_summarize(args)

    out = json.loads(capsys.readouterr().out)
    assert out["total_events"] == 0
    assert out["days"] == []


def test_calendar_summarize_week_flag_targets_next_monday(api_module, capsys, monkeypatch):
    """--week mode requests next Mon–Sun, not today+7."""
    captured_params = {}

    def capture_run(cmd, **kwargs):
        if "--params" in cmd:
            captured_params.update(json.loads(cmd[cmd.index("--params") + 1]))
        return MagicMock(returncode=0, stdout=json.dumps({"items": []}), stderr="")

    args = api_module.argparse.Namespace(
        week=True, days=7, calendar="primary", format="json",
        func=api_module.calendar_summarize,
    )

    with patch.object(api_module.subprocess, "run", side_effect=capture_run):
        api_module.calendar_summarize(args)

    # timeMin should be on a Monday (weekday == 0)
    time_min = captured_params.get("timeMin", "")
    assert time_min, "timeMin not captured"
    dt = datetime.fromisoformat(time_min)
    assert dt.weekday() == 0, f"Expected Monday (0), got weekday {dt.weekday()} for {time_min}"


def test_calendar_summarize_all_day_event(api_module, capsys):
    """All-day events (date-only, no T) are handled without crash."""
    all_day = [
        {
            "id": "allday1",
            "summary": "Company Holiday",
            "start": {"date": "2026-07-24"},
            "end": {"date": "2026-07-25"},
            "location": "",
            "description": "",
            "status": "confirmed",
            "htmlLink": "",
        }
    ]
    args = api_module.argparse.Namespace(
        week=False, days=7, calendar="primary", format="json",
        func=api_module.calendar_summarize,
    )

    with patch.object(api_module.subprocess, "run", side_effect=_fake_gws_events(all_day)):
        api_module.calendar_summarize(args)

    out = json.loads(capsys.readouterr().out)
    assert out["total_events"] == 1
    assert out["days"][0]["events"][0]["time"] == "all-day"

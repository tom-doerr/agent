import re

import context_provider as cp


def test_context_includes_weekday_in_datetime_line(monkeypatch):
    # Keep external calls quiet for the test
    monkeypatch.setattr(cp, "get_weather_info", lambda: "ok")
    monkeypatch.setattr(cp, "get_home_status", lambda: "")
    monkeypatch.setattr(cp, "get_post_queue_status", lambda: "")
    monkeypatch.setattr(cp, "get_autoposter_alert", lambda: "")
    monkeypatch.setattr(cp, "get_system_info", lambda: "")

    ctx = cp.create_context_string()
    first_line = ctx.splitlines()[0]
    # Expect: Datetime: YYYY-MM-DD HH:MM:SS (Weekday)
    assert first_line.startswith("Datetime: ")
    assert "(" in first_line and ")" in first_line
    inside = first_line[first_line.find("(") + 1 : first_line.rfind(")")]
    assert re.search(r"[A-Za-z]", inside)


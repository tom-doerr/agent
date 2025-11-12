from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from uuid import uuid4
import json


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient

from webapp.nlco_htmx.app import WebConfig, create_app
from webapp.nlco_htmx import utils
import asyncio


@pytest.fixture()
def temp_paths(tmp_path: Path) -> dict[str, Path]:
    artifact = tmp_path / "artifact.md"
    artifact.write_text("Artifact snapshot", encoding="utf-8")
    memory = tmp_path / "memory.md"
    memory.write_text("Memory baseline", encoding="utf-8")
    short_term = tmp_path / "short_term_memory.md"
    short_term.write_text("Short-term memo", encoding="utf-8")
    constraints = tmp_path / "constraints.md"
    constraints.write_text("# 2025-10-04\n2100 Earlier entry\n", encoding="utf-8")
    schedule = tmp_path / "structured_schedule.json"
    schedule.write_text(
        json.dumps(
            [
                {
                    "start_time": "2025-10-07 18:30",
                    "end_time": "2025-10-07 19:00",
                    "description": "Dinner",
                },
                {
                    "start_time": "2025-10-07 19:30",
                    "end_time": "2025-10-07 20:00",
                    "description": "Study session",
                },
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "artifact": artifact,
        "memory": memory,
        "short_term": short_term,
        "constraints": constraints,
        "schedule": schedule,
    }


def register_and_login(client: TestClient, email: str, password: str) -> None:
    register_response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/auth/jwt/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code in (200, 204)


def build_app(temp_paths: dict[str, Path], **overrides):
    auth_db = temp_paths["artifact"].parent / f"auth-{uuid4().hex}.db"
    kwargs = dict(
        artifact_path=temp_paths["artifact"],
        memory_path=temp_paths["memory"],
        short_term_memory_path=temp_paths.get("short_term"),
        constraints_path=temp_paths["constraints"],
        schedule_path=temp_paths["schedule"],
        history_limit=10,
        auth_database_url=f"sqlite+aiosqlite:///{auth_db.as_posix()}",
        auth_jwt_secret="test-secret",
    )
    kwargs.update(overrides)
    app = create_app(WebConfig(**kwargs))
    asyncio.run(app.state.auth_context.startup())
    return app


@pytest.fixture()
def client(temp_paths: dict[str, Path]) -> TestClient:
    app = build_app(temp_paths)
    with TestClient(app) as client:
        register_and_login(client, f"user-{uuid4().hex}@example.com", "Passw0rd!")
        yield client


def make_client(temp_paths: dict[str, Path], **overrides) -> TestClient:
    app = build_app(temp_paths, **overrides)
    client = TestClient(app)
    register_and_login(client, f"user-{uuid4().hex}@example.com", "Passw0rd!")
    return client


def test_requires_login_when_not_authenticated(temp_paths: dict[str, Path]) -> None:
    app = build_app(temp_paths)
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        text = response.text
        assert "Sign in to NLCO" in text
        assert 'id="login-form"' in text


def test_requires_auth_for_partials(temp_paths: dict[str, Path]) -> None:
    app = build_app(temp_paths)
    with TestClient(app) as client:
        resp = client.get("/partials/history")
        assert resp.status_code == 401
        resp = client.post("/messages", data={"message": "unauthorized"})
        assert resp.status_code == 401


def test_login_page_shows_github_link(temp_paths: dict[str, Path]) -> None:
    overrides = {
        "github_client_id": "fake-id",
        "github_client_secret": "fake-secret",
        "github_redirect_url": "http://testserver/auth/github/callback",
    }
    app = build_app(temp_paths, **overrides)
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        text = response.text
        assert "Continue with GitHub" in text
        assert "/auth/github/login" in text
        assert 'id="login-form"' in text


def test_index_renders_artifact_memory_and_history(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    text = response.text
    assert "Artifact snapshot" in text
    assert "Memory baseline" in text
    assert "Short-term memo" in text
    assert "# 2025-10-04" in text
    assert "2100 Earlier entry" in text
    assert "onkeydown=\"if(event.key==='Enter'" in text
    assert "hx-on::after-settle=\"const list=" in text
    assert "<h2>Schedule</h2>" in text
    assert "Dinner" in text
    assert "Study session" in text


def test_post_message_appends_with_timestamp(client: TestClient, temp_paths: dict[str, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            return cls(2025, 10, 5, 21, 15, 0)

    monkeypatch.setattr("webapp.nlco_htmx.app.datetime", FixedDatetime)

    response = client.post("/messages", data={"message": "new constraint"})
    assert response.status_code == 200
    updated = temp_paths["constraints"].read_text(encoding="utf-8")
    assert "# 2025-10-05" in updated
    assert "2115 new constraint" in updated
    assert "2115 new constraint" in response.text


def test_history_limit_applied(temp_paths: dict[str, Path]) -> None:
    constraints = temp_paths["constraints"]
    for i in range(20):
        utils.write_constraints_entry(
            constraints,
            f"entry {i}",
            now=datetime(2025, 10, 5, 12, i, 0),
        )

    client = make_client(temp_paths, history_limit=5)
    try:
        response = client.get("/partials/history")
        assert response.status_code == 200
        text = response.text
        assert "entry 19" in text
        assert "entry 14" not in text
    finally:
        client.close()


def test_artifact_partial_contains_latest_snapshot(client: TestClient) -> None:
    response = client.get("/partials/artifact")
    assert response.status_code == 200
    text = response.text
    assert "Artifact snapshot" in text
    assert "Updated" in text


def test_schedule_partial_renders_table(client: TestClient) -> None:
    response = client.get("/partials/schedule")
    assert response.status_code == 200
    text = response.text
    assert "<table" in text
    assert "Dinner" in text
    assert "Study session" in text
    assert "2025-10-07 18:30" in text


def test_schedule_partial_handles_invalid_json(temp_paths: dict[str, Path]) -> None:
    bad_schedule = temp_paths["schedule"].parent / "bad_schedule.json"
    bad_schedule.write_text("{invalid json", encoding="utf-8")
    client = make_client(temp_paths, schedule_path=bad_schedule)
    try:
        response = client.get("/partials/schedule")
        assert response.status_code == 200
        text = response.text
        assert "Unable to parse schedule" in text
        assert "No structured schedule captured yet." in text
    finally:
        client.close()


def test_memory_partial_includes_short_term(client: TestClient) -> None:
    response = client.get("/partials/memory")
    assert response.status_code == 200
    text = response.text
    assert "Memory baseline" in text
    assert "Short-term memo" in text
    assert "Short-Term Memory" in text


def test_memory_partial_without_short_term(temp_paths: dict[str, Path]) -> None:
    client = make_client(temp_paths, short_term_memory_path=None)
    try:
        response = client.get("/partials/memory")
        assert response.status_code == 200
        text = response.text
        assert "Short-Term Memory" in text
        assert "never" in text
    finally:
        client.close()


def test_post_message_requires_nonempty_input(client: TestClient) -> None:
    response = client.post("/messages", data={"message": "   "})
    assert response.status_code == 400


def test_api_requires_auth(temp_paths: dict[str, Path]) -> None:
    app = build_app(temp_paths)
    with TestClient(app) as client:
        resp = client.get("/api/v1/status")
        assert resp.status_code == 401
        resp = client.post("/api/v1/messages", json={"message": "hi"})
        assert resp.status_code == 401


def test_api_status_returns_payload(client: TestClient) -> None:
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["artifact"]["text"].startswith("Artifact snapshot")
    assert data["memory"]["text"] == "Memory baseline"
    assert data["short_term_memory"]["text"] == "Short-term memo"
    history = data["history"]
    assert isinstance(history, list)
    assert history[-1]["entries"][-1].endswith("Earlier entry")
    schedule = data["schedule"]
    assert len(schedule["blocks"]) == 2
    assert schedule["blocks"][0]["description"] == "Dinner"
    assert schedule["age_label"].endswith("ago") or schedule["age_label"] == "never"


def test_api_post_message_updates_history(
    client: TestClient,
    temp_paths: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            return cls(2025, 10, 5, 21, 30, 0)

    monkeypatch.setattr("webapp.nlco_htmx.app.datetime", FixedDatetime)

    resp = client.post("/api/v1/messages", json={"message": "android app test"})
    assert resp.status_code == 200
    data = resp.json()
    history = data["history"]
    assert history[-1]["entries"][-1] == "2130 android app test"
    updated = temp_paths["constraints"].read_text(encoding="utf-8")
    assert "2130 android app test" in updated
    assert data["schedule"]["blocks"][0]["description"] == "Dinner"

def test_default_user_created_from_env(temp_paths: dict[str, Path]) -> None:
    overrides = {
        "default_user_email": "owner@nlco.dev",
        "default_user_password": "Sup3rSecure!",
    }
    app = build_app(temp_paths, **overrides)
    with TestClient(app) as client:
        response = client.post(
            "/auth/jwt/login",
            data={"username": overrides["default_user_email"], "password": overrides["default_user_password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code in (200, 204)
        status_resp = client.get("/api/v1/status")
        assert status_resp.status_code == 200
        payload = status_resp.json()
        assert payload["artifact"]["text"].startswith("Artifact")

def test_default_user_login_short_username(temp_paths: dict[str, Path]) -> None:
    overrides = {
        "default_user_email": "owner@nlco.dev",
        "default_user_password": "Sup3rSecure!",
    }
    app = build_app(temp_paths, **overrides)
    with TestClient(app) as client:
        resp = client.post(
            "/auth/jwt/login",
            data={"username": "owner", "password": overrides["default_user_password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code in (200, 204)
        status_resp = client.get("/api/v1/status")
        assert status_resp.status_code == 200


def test_load_schedule_snapshot_success(temp_paths: dict[str, Path]) -> None:
    blocks, mtime, error = utils.load_schedule_snapshot(temp_paths["schedule"])
    assert error is None
    assert len(blocks) == 2
    assert blocks[0].description == "Dinner"
    assert mtime is not None


def test_load_schedule_snapshot_invalid_json(tmp_path: Path) -> None:
    schedule = tmp_path / "broken.json"
    schedule.write_text("{oops", encoding="utf-8")
    blocks, mtime, error = utils.load_schedule_snapshot(schedule)
    assert blocks == []
    assert mtime is not None
    assert error and "Unable to parse schedule" in error

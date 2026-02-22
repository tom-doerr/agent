"""Tests for router module."""

from actor_tui_pkg.router import Router, RouterSignature


def test_router_signature_fields():
    fields = RouterSignature.fields
    assert "route" in fields
    assert "reasoning" in fields
    assert "user_message" in fields


def test_router_init():
    r = Router()
    assert r.predict is not None

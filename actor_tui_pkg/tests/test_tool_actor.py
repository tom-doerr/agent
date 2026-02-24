"""Tests for tool_actor module."""

import pytest
from pydantic import ValidationError

from actor_tui_pkg.tool_actor import (
    ALLOWED_COMMANDS,
    ToolCommand,
    ToolSignature,
    ToolResultSignature,
    validate_command,
    execute_safe_command,
)


def test_validate_ls():
    ok, err = validate_command("ls -la /home")
    assert ok is True

def test_validate_head():
    ok, err = validate_command("head -n 20 /etc/hosts")
    assert ok is True

def test_validate_tail():
    ok, err = validate_command("tail -5 /etc/hosts")
    assert ok is True

def test_reject_rm():
    ok, err = validate_command("rm -rf /")
    assert ok is False

def test_reject_pipe():
    ok, err = validate_command("ls | cat")
    assert ok is False

def test_reject_semicolon():
    ok, err = validate_command("ls; rm -rf /")
    assert ok is False

def test_reject_backtick():
    ok, err = validate_command("ls `whoami`")
    assert ok is False

def test_reject_dollar():
    ok, err = validate_command("ls $HOME")
    assert ok is False

def test_reject_empty():
    ok, err = validate_command("")
    assert ok is False

def test_reject_path_bypass():
    ok, err = validate_command("/usr/bin/rm file")
    assert ok is False

def test_execute_safe_ls(tmp_path):
    (tmp_path / "hello.txt").write_text("hi")
    output = execute_safe_command(f"ls {tmp_path}")
    assert "hello.txt" in output

def test_execute_blocked():
    output = execute_safe_command("rm -rf /")
    assert "BLOCKED" in output

def test_tool_command_valid():
    cmd = ToolCommand(command="ls -la /tmp")
    assert cmd.command == "ls -la /tmp"

def test_tool_command_rejected():
    with pytest.raises(ValidationError):
        ToolCommand(command="rm -rf /")

def test_tool_signature_fields():
    fields = ToolSignature.fields
    assert "commands" in fields
    assert "summary" in fields

def test_tool_result_signature_fields():
    fields = ToolResultSignature.fields
    assert "reply" in fields


def test_execute_tilde_expansion():
    import os
    out = execute_safe_command("ls ~")
    assert "BLOCKED" not in out
    assert "ERROR" not in out

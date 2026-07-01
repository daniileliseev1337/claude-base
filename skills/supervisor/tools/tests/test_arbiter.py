# tests/test_arbiter.py — proves the arbiter maps decide() to SDK allow/deny
import asyncio
from arbiter import can_use_tool
from claude_agent_sdk import PermissionResultAllow, PermissionResultDeny

def test_safe_read_allows():
    r = asyncio.run(can_use_tool("Read", {"file_path": "x"}, None))
    assert isinstance(r, PermissionResultAllow)

def test_safe_bash_allows():
    r = asyncio.run(can_use_tool("Bash", {"command": "git status"}, None))
    assert isinstance(r, PermissionResultAllow)

def test_force_push_denies():
    r = asyncio.run(can_use_tool("Bash", {"command": "git push --force origin main"}, None))
    assert isinstance(r, PermissionResultDeny)

def test_unknown_tool_denies():
    r = asyncio.run(can_use_tool("SomeUnknownTool", {}, None))
    assert isinstance(r, PermissionResultDeny)


def test_decide_error_denies(monkeypatch):
    # fail-safe: if decide() raises, the arbiter denies by default (never silent-allow)
    import arbiter
    def _boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(arbiter, "decide", _boom)
    r = asyncio.run(arbiter.can_use_tool("Read", {"file_path": "x"}, None))
    assert isinstance(r, PermissionResultDeny)

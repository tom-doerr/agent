import json
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.no_memory_stub
@pytest.mark.skipif(
    not any(
        os.environ.get(var)
        for var in (
            "OPENROUTER_API_KEY",
            "OPENAI_API_KEY",
        )
    ),
    reason="Requires OpenRouter/OpenAI credentials for live DSPy inference.",
)
def test_e2e_memory_summary(tmp_path):
    cache_dir = tmp_path / "dspy_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    python_snippet = textwrap.dedent(
        """
        import json
        import agent_manual_pkg.runtime as runtime
        from agent_manual_pkg import memory

        runtime.configure_model("chat", persist=False)
        updates = memory.MEMORY_MODULE(
            prompt="Team planning session",
            steps=[
                {
                    "thought": "Summarize the plan",
                    "tool": "run_shell",
                    "args": {"command": "ls"},
                    "observation": {"status": "ok", "command": "ls", "output": "README.md"},
                }
            ],
        )
        print(json.dumps([u.model_dump() for u in updates]))
        """
    ).strip()

    shell_cmd = "\n".join(
        [
            f"cd {ROOT}",
            f"export PYTHONPATH=\"{(ROOT / 'agent_manual_pkg' / 'src').as_posix()}:$PYTHONPATH\"",
            f"export DSPY_CACHEDIR=\"{cache_dir}\"",
            "python - <<'PY'",
            python_snippet,
            "PY",
        ]
    )

    proc = subprocess.run(
        ["zsh", "-ic", shell_cmd],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    raw = lines[-1]
    start = raw.find('[')
    payload = json.loads(raw[start:])
    assert isinstance(payload, list) and payload
    assert all("action" in item for item in payload)


def test_e2e_tui_help_toggle(tmp_path):
    cache_dir = tmp_path / "dspy_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    python_snippet = textwrap.dedent(
        """
        import asyncio
        from agent_manual_pkg import app as agent_app

        async def main() -> None:
            tui = agent_app.TUI(concurrency=0)
            async with tui.run_test() as pilot:
                await pilot.press("#in", "escape")
                await pilot.press("question_mark")
                await pilot.pause(0.05)
                print(type(tui.screen).__name__)

        asyncio.run(main())
        """
    ).strip()

    shell_cmd = "\n".join(
        [
            f"cd {ROOT}",
            f"export PYTHONPATH=\"{(ROOT / 'agent_manual_pkg' / 'src').as_posix()}:$PYTHONPATH\"",
            f"export DSPY_CACHEDIR=\"{cache_dir}\"",
            "python - <<'PY'",
            python_snippet,
            "PY",
        ]
    )

    proc = subprocess.run(
        ["zsh", "-ic", shell_cmd],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )

    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    assert "HelpScreen" in lines

"""Tests for the setup_env.sh helper script."""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_SOURCE = PROJECT_ROOT / "setup_env.sh"


def _prepare_script(temp_dir: Path) -> Path:
    """Copy the setup script and create a minimal requirements file."""

    script_path = temp_dir / "setup_env.sh"
    script_path.write_text(SCRIPT_SOURCE.read_text())
    script_path.chmod(script_path.stat().st_mode | stat.S_IXUSR)

    requirements = temp_dir / "requirements.txt"
    requirements.write_text("# empty requirements for tests\n")
    return script_path


def _run_setup(script_path: Path, *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Execute the setup script and return the completed process."""

    merged_env = os.environ.copy()
    merged_env.update(env)

    return subprocess.run(
        [str(script_path)],
        cwd=script_path.parent,
        check=True,
        text=True,
        capture_output=True,
        env=merged_env,
    )


def test_setup_env_uses_uv_when_available(tmp_path: Path) -> None:
    """Ensure the script prefers uv when it is available on PATH."""

    script_path = _prepare_script(tmp_path)

    uv_log = tmp_path / "uv.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    uv_script = bin_dir / "uv"
    uv_script.write_text(
        f"#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" >> '{uv_log}'\n"
    )
    uv_script.chmod(uv_script.stat().st_mode | stat.S_IXUSR)

    result = _run_setup(
        script_path,
        env={
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "PYTHON": sys.executable,
            "PIP_NO_INDEX": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        },
    )

    assert "Environment setup complete." in result.stdout
    assert uv_log.exists(), result.stderr
    log_content = uv_log.read_text().strip()
    assert "pip" in log_content and "--python" in log_content

    venv_python = script_path.parent / ".venv" / "bin" / "python"
    assert venv_python.exists()

    env_example = script_path.parent / ".env.example"
    assert env_example.exists()
    example_contents = env_example.read_text()
    assert "OPENROUTER_API_KEY=" in example_contents


def test_setup_env_falls_back_to_python3_and_pip(tmp_path: Path) -> None:
    """Verify the script handles missing interpreters and uv failures."""

    script_path = _prepare_script(tmp_path)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    # Stub python interpreter that fails so the script must fall back to python3.
    failing_python = bin_dir / "python3.11"
    failing_python.write_text("#!/usr/bin/env bash\nexit 1\n")
    failing_python.chmod(failing_python.stat().st_mode | stat.S_IXUSR)

    # Stub uv command that always fails to trigger the pip fallback path.
    uv_log = tmp_path / "uv_failed.log"
    uv_script = bin_dir / "uv"
    uv_script.write_text(
        f"#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" >> '{uv_log}'\n"
        "exit 1\n"
    )
    uv_script.chmod(uv_script.stat().st_mode | stat.S_IXUSR)

    result = _run_setup(
        script_path,
        env={
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "PYTHON": str(failing_python),
            "PIP_NO_INDEX": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        },
    )

    # The script should report that it fell back to python3 and pip.
    assert "falling back to python3" in result.stderr
    assert "uv pip install failed, falling back to pip" in result.stderr

    assert uv_log.exists()
    assert (script_path.parent / ".venv" / "bin" / "python").exists()

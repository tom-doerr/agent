from pathlib import Path

import timestamp_app_core as core
import nlco_iter


def test_headless_uses_shared_artifact_resolver():
    # Default constant should track the shared resolver path
    assert Path(nlco_iter.ARTIFACT_FILE) == core.resolve_artifact_path()


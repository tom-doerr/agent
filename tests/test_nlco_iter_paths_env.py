from pathlib import Path

import timestamp_app_core as core
import nlco_iter


def test_headless_uses_shared_resolvers():
    # Default constants should track the shared resolver paths
    assert Path(nlco_iter.ARTIFACT_FILE) == core.resolve_artifact_path()
    assert Path(nlco_iter.CONSTRAINTS_FILE) == core.resolve_constraints_path()
    assert Path(nlco_iter.MEMORY_FILE) == core.resolve_memory_path()
    assert Path(nlco_iter.SHORT_TERM_FILE) == core.resolve_short_term_path()

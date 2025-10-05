import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_get_post_queue_status_counts_posts(tmp_path):
    from context_provider import get_post_queue_status, config

    queue_file = tmp_path / "saved_posts.json"
    queue_data = [
        {"repo_name": "example/repo1"},
        {"repo_name": "example/repo2"},
    ]
    queue_file.write_text(json.dumps(queue_data))

    original_path = config.social.post_queue_path
    config.social.post_queue_path = queue_file

    try:
        status = get_post_queue_status()
    finally:
        config.social.post_queue_path = original_path

    assert "2 posts remaining" in status


def test_get_autoposter_alert_when_stale(tmp_path):
    from context_provider import get_autoposter_alert, config

    posted_file = tmp_path / "posted_posts.json"
    posted_file.write_text("[]")

    stale_time = datetime.now(timezone.utc) - timedelta(minutes=40)
    timestamp = stale_time.timestamp()
    os.utime(posted_file, times=(timestamp, timestamp))

    original_path = config.social.posted_posts_path
    config.social.posted_posts_path = posted_file

    try:
        alert = get_autoposter_alert()
    finally:
        config.social.posted_posts_path = original_path

    assert "Autoposter alert" in alert

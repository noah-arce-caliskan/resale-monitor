from zoneinfo import ZoneInfo

from resale_monitor.worker import create_scheduler


def test_worker_scheduler_uses_utc() -> None:
    scheduler = create_scheduler()

    assert scheduler.timezone == ZoneInfo("UTC")

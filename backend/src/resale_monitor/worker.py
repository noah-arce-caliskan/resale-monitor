from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler


def create_scheduler() -> BlockingScheduler:
    return BlockingScheduler(timezone=ZoneInfo("UTC"))


def main() -> None:
    create_scheduler().start()


if __name__ == "__main__":  # pragma: no cover
    main()

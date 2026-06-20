import sys
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
try:
    from .pipeline import run_daily
    from .logging_config import setup_logging
except ImportError:
    ROOT_DIR = Path(__file__).resolve().parent
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
    from pipeline import run_daily
    from logging_config import setup_logging
import signal

logger = setup_logging()

sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=2)
def daily_job():
    logger.info("Scheduled job triggered: daily_job")
    run_daily()


def _shutdown(signum, frame):
    logger.info("Shutting down scheduler")
    try:
        sched.shutdown(wait=False)
    except Exception:
        pass
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)
    logger.info("Starting scheduler (CTRL+C to exit)")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        _shutdown(None, None)

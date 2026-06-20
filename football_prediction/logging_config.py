import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler


def setup_logging(config=None):
    log_dir = os.environ.get("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
        root.addHandler(logging.StreamHandler())
        root.addHandler(handler)

    # library noise reduction
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    return logging.getLogger(__name__)

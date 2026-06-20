import importlib
import logging
import os
import sys
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from .logging_config import setup_logging
except ImportError:
    from logging_config import setup_logging

logger = setup_logging()

MODEL_OUTPUT = Path(os.environ.get("MODEL_OUTPUT_DIR", str(BASE_DIR / "models_output")))
MODEL_OUTPUT.mkdir(parents=True, exist_ok=True)


def update_data():
    logger.info("Updating data: calling scrapers if present")
    try:
        # attempt to call known scrapers if they exist
        scrapers = [
            "scrapers.fbref_scraper",
            "scrapers.football_data_scraper",
            "scrapers.odds_scraper",
            "scrapers.understat_scraper",
        ]
        for mod in scrapers:
            try:
                m = importlib.import_module(mod)
                if hasattr(m, "run"):
                    logger.info(f"Running {mod}.run()")
                    m.run()
            except Exception as e:
                logger.warning(f"Could not run {mod}: {e}")
    except Exception:
        logger.exception("Error during update_data")


def train_all_models():
    logger.info("Discovering model modules in 'models' package")
    models_dir = BASE_DIR / "models"
    if not models_dir.exists():
        logger.warning("No models directory found")
        return

    for py in models_dir.glob("*_model.py"):
        name = py.stem
        try:
            mod = importlib.import_module(f"{BASE_DIR.name}.models.{name}")
            if hasattr(mod, "train"):
                logger.info(f"Training model: {name}")
                model_obj, metrics = mod.train()
                model_path = MODEL_OUTPUT / f"{name}.joblib"
                joblib.dump(model_obj, model_path)
                logger.info(f"Saved model to {model_path}")
                # save metadata if DB available
                try:
                    from db import get_session, save_model_metadata
                    session = get_session()
                    save_model_metadata(session, name=name, path=str(model_path), metrics=metrics)
                except Exception:
                    logger.debug("DB not available or failed to save metadata")
            else:
                logger.debug(f"No train() in {name}")
        except Exception:
            logger.exception(f"Failed training {name}")


def run_daily():
    logger.info("Starting daily pipeline: update_data -> train_all_models")
    try:
        update_data()
        train_all_models()
    except Exception:
        logger.exception("run_daily failed")


if __name__ == "__main__":
    run_daily()

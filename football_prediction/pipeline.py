import importlib
import logging
import os
import pkgutil
import sys
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from . import scrapers as scrapers_pkg
    from .config_loader import get_data_sources, load_config
    from .logging_config import setup_logging
    from .data_loader import load_upcoming_matches
    from .prediction_service import predict_matches
except ImportError:
    from scrapers import scrapers as scrapers_pkg
    from config_loader import get_data_sources, load_config
    from logging_config import setup_logging
    from data_loader import load_upcoming_matches
    from prediction_service import predict_matches

logger = setup_logging()

MODEL_OUTPUT = Path(os.environ.get("MODEL_OUTPUT_DIR", str(BASE_DIR / "data" / "models")))
MODEL_OUTPUT.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def update_data():
    logger.info("Updating data: calling scrapers if present")
    try:
        config = load_config()
        data_sources = get_data_sources(config)

        for finder, name, ispkg in pkgutil.iter_modules(scrapers_pkg.__path__):
            if name.startswith("_"):
                continue

            module_name = f"{scrapers_pkg.__name__}.{name}"
            try:
                module = importlib.import_module(module_name)
                if not hasattr(module, "run"):
                    logger.debug(f"Skipping scraper module without run(): {module_name}")
                    continue

                source_name = getattr(module, "SOURCE_NAME", name)
                source_config = data_sources.get(source_name, {})
                if not source_config.get("enabled", False):
                    logger.debug(f"Skipping disabled scraper source: {source_name}")
                    continue

                logger.info(f"Running scraper for source {source_name}: {module_name}")
                module.run()
            except Exception as e:
                logger.warning(f"Could not run scraper module {module_name}: {e}")
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


def generate_predictions():
    logger.info("Generating predictions for upcoming matches")
    try:
        matches = load_upcoming_matches()
        if not matches:
            logger.warning("Aucun match à venir trouvé, aucune prédiction générée.")
            return

        predictions = predict_matches(matches)
        df = pd.DataFrame(predictions)
        latest_path = PROCESSED_DIR / "predictions.csv"
        dated_path = PROCESSED_DIR / f"predictions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(latest_path, index=False)
        df.to_csv(dated_path, index=False)
        logger.info(f"Predictions sauvegardées: {latest_path} et {dated_path}")
    except Exception:
        logger.exception("Erreur lors de la génération des prédictions")


def run_daily():
    logger.info("Starting daily pipeline: update_data -> train_all_models -> generate_predictions")
    try:
        update_data()
        train_all_models()
        generate_predictions()
    except Exception:
        logger.exception("run_daily failed")


if __name__ == "__main__":
    run_daily()

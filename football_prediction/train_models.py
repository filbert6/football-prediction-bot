"""Script pour entraîner et sauvegarder les modèles."""
import sys
import importlib
import joblib
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(BASE_DIR.parent))

try:
    from .logging_config import setup_logging
except ImportError:
    from logging_config import setup_logging

logger = setup_logging()

MODEL_OUTPUT = BASE_DIR / "models_output"
DATA_MODEL_DIR = BASE_DIR / "data" / "models"
MODEL_OUTPUT.mkdir(parents=True, exist_ok=True)
DATA_MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_and_save_models():
    """Entraîne et sauvegarde tous les modèles."""
    logger.info("=== Début de l'entraînement des modèles ===")
    models = [
        "dummy_model",
        "poisson_model",
        "random_forest_model",
        "xgboost_model",
        "lightgbm_model",
        "ensemble_model",
    ]

    success = True
    for name in models:
        try:
            module = importlib.import_module(f"football_prediction.models.{name}")
            if hasattr(module, "train"):
                logger.info(f"Entraînement du modèle {name}...")
                model, metrics = module.train()
                for target_dir in [MODEL_OUTPUT, DATA_MODEL_DIR]:
                    model_path = target_dir / f"{name}.joblib"
                    joblib.dump(model, model_path)
                    logger.info(f"Modèle sauvegardé: {model_path}")
                logger.info(f"Métriques {name}: {metrics}")
            else:
                logger.warning(f"Module {name} ne contient pas de fonction train().")
        except Exception as e:
            logger.exception(f"Erreur lors de l'entraînement de {name}: {e}")
            success = False

    logger.info("=== Entraînement terminé ===")
    return success


if __name__ == "__main__":
    success = train_and_save_models()
    sys.exit(0 if success else 1)

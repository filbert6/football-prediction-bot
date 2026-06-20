"""Script pour entraîner et sauvegarder les modèles."""
import sys
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
MODEL_OUTPUT.mkdir(parents=True, exist_ok=True)


def train_and_save_models():
    """Entraîne et sauvegarde tous les modèles."""
    logger.info("=== Début de l'entraînement des modèles ===")
    
    try:
        # Entraîner le modèle dummy
        from .models.dummy_model import train as train_dummy
        logger.info("Entraînement du modèle dummy...")
        model, metrics = train_dummy()
        
        # Sauvegarder le modèle
        model_path = MODEL_OUTPUT / "dummy_model.joblib"
        joblib.dump(model, model_path)
        logger.info(f"Modèle sauvegardé: {model_path}")
        logger.info(f"Métriques: {metrics}")
        
        logger.info("=== Entraînement complété avec succès ===")
        return True
    except Exception as e:
        logger.exception(f"Erreur lors de l'entraînement: {e}")
        return False


if __name__ == "__main__":
    success = train_and_save_models()
    sys.exit(0 if success else 1)

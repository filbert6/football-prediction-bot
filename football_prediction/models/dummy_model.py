"""Modèle de démonstration simple."""
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class DummyClassifier:
    """Classifieur simple pour démonstration."""
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.classes_ = np.array([0, 1, 2])  # 0: Home, 1: Draw, 2: Away
    
    def fit(self, X, y=None):
        """Entraîner le modèle (dummy ne fait rien)."""
        return self
    
    def predict(self, X):
        """Prédire."""
        np.random.seed(self.random_state)
        return np.random.randint(0, 3, size=len(X))
    
    def predict_proba(self, X):
        """Retourner les probabilités."""
        np.random.seed(self.random_state)
        # Générer des probabilités aléatoires mais réalistes
        proba = np.random.dirichlet([1, 1, 1], size=len(X))
        return proba


def train():
    """Entraîne le modèle dummy."""
    logger.info("Entraînement du modèle dummy")
    
    # Générer des données de démonstration
    X_train = np.random.randn(100, 10)
    y_train = np.random.randint(0, 3, 100)
    
    model = DummyClassifier()
    model.fit(X_train, y_train)
    
    # Métriques fictives
    metrics = {
        "accuracy": 0.65,
        "precision": 0.63,
        "recall": 0.64,
        "f1": 0.62
    }
    
    logger.info(f"Modèle entraîné avec métriques: {metrics}")
    return model, metrics

#!/usr/bin/env python
"""Script pour entraîner les modèles du bot de prédiction."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from football_prediction.train_models import train_and_save_models

if __name__ == "__main__":
    print("🤖 Entraînement des modèles de prédiction...")
    success = train_and_save_models()
    
    if success:
        print("✅ Modèles entraînés et sauvegardés avec succès!")
        sys.exit(0)
    else:
        print("❌ Erreur lors de l'entraînement des modèles")
        sys.exit(1)

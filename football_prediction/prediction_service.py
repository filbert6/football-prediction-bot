"""Service de prédiction avec chargement réel des modèles."""
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODEL_OUTPUT = BASE_DIR / "models_output"
DATA_MODEL_OUTPUT = BASE_DIR / "data" / "models"
MODEL_OUTPUT.mkdir(parents=True, exist_ok=True)
DATA_MODEL_OUTPUT.mkdir(parents=True, exist_ok=True)


class PredictionService:
    """Service pour charger les modèles et générer des prédictions."""
    
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.model_metadata = {}
        self.load_models()
    
    def load_models(self) -> None:
        """Charge tous les modèles disponibles."""
        try:
            loaded = set()
            for models_dir in [MODEL_OUTPUT, DATA_MODEL_OUTPUT]:
                if not models_dir.exists():
                    continue
                for model_path in models_dir.glob("*.joblib"):
                    model_name = model_path.stem
                    if model_name in loaded:
                        continue
                    try:
                        model = joblib.load(model_path)
                        self.models[model_name] = model
                        loaded.add(model_name)
                        logger.info(f"Modèle chargé: {model_name} depuis {models_dir}")
                    except Exception as e:
                        logger.warning(f"Impossible de charger {model_path}: {e}")
            
            for scaler_dir in [MODEL_OUTPUT, DATA_MODEL_OUTPUT]:
                scaler_path = scaler_dir / "scaler.joblib"
                if scaler_path.exists():
                    self.scaler = joblib.load(scaler_path)
                    logger.info(f"Scaler chargé depuis {scaler_dir}")
                    break
            
            if not self.models:
                logger.warning("Aucun modèle trouvé. Les prédictions seront factices.")
        except Exception as e:
            logger.exception(f"Erreur lors du chargement des modèles: {e}")
    
    def prepare_features(self, match_data: Dict) -> np.ndarray:
        """Prépare les features pour une prédiction."""
        # Features de base pour une prédiction
        features = [
            match_data.get("home_elo", 1600),
            match_data.get("away_elo", 1600),
            match_data.get("home_form", 0.5),
            match_data.get("away_form", 0.5),
            match_data.get("home_attack", 0.5),
            match_data.get("away_attack", 0.5),
            match_data.get("home_defense", 0.5),
            match_data.get("away_defense", 0.5),
            match_data.get("home_h2h", 0.5),
            match_data.get("away_h2h", 0.5),
        ]
        return np.array(features).reshape(1, -1)
    
    def predict_match(self, match_data: Dict) -> Dict:
        """Prédit le résultat d'un match."""
        try:
            features = self.prepare_features(match_data)
            
            predictions = {}
            
            # Si des modèles sont disponibles, les utiliser
            if self.models:
                for model_name, model in self.models.items():
                    try:
                        pred = model.predict(features)
                        if hasattr(model, 'predict_proba'):
                            proba = model.predict_proba(features)[0]
                            predictions[model_name] = {
                                'prediction': pred[0],
                                'probabilities': proba.tolist() if len(proba) == 3 else None
                            }
                        else:
                            predictions[model_name] = {'prediction': pred[0]}
                    except Exception as e:
                        logger.warning(f"Erreur avec modèle {model_name}: {e}")
            else:
                # Génération factice basée sur les odds
                home_odds = match_data.get("home_odds", 2.0)
                away_odds = match_data.get("away_odds", 3.0)
                draw_odds = match_data.get("draw_odds", 3.2)
                
                # Conversion des cotes en probabilités implicites
                total = 1/home_odds + 1/away_odds + 1/draw_odds
                home_prob = (1/home_odds) / total * 100
                draw_prob = (1/draw_odds) / total * 100
                away_prob = (1/away_odds) / total * 100
                
                predictions['factice'] = {
                    'home_win': home_prob,
                    'draw': draw_prob,
                    'away_win': away_prob
                }
            
            return self._aggregate_predictions(predictions, match_data)
        except Exception as e:
            logger.exception(f"Erreur lors de la prédiction: {e}")
            return self._fallback_prediction(match_data)
    
    def _aggregate_predictions(self, predictions: Dict, match_data: Dict) -> Dict:
        """Agrège les prédictions de plusieurs modèles."""
        if not predictions:
            return self._fallback_prediction(match_data)
        
        # Moyenne des prédictions si plusieurs modèles
        if len(predictions) > 1:
            home_wins = []
            draws = []
            away_wins = []
            
            for model_pred in predictions.values():
                if 'probabilities' in model_pred and model_pred['probabilities']:
                    home_wins.append(model_pred['probabilities'][0] * 100)
                    draws.append(model_pred['probabilities'][1] * 100)
                    away_wins.append(model_pred['probabilities'][2] * 100)
                elif 'home_win' in model_pred:
                    home_wins.append(model_pred['home_win'])
                    draws.append(model_pred['draw'])
                    away_wins.append(model_pred['away_win'])
            
            if home_wins:
                home_prob = np.mean(home_wins)
                draw_prob = np.mean(draws)
                away_prob = np.mean(away_wins)
            else:
                return self._fallback_prediction(match_data)
        else:
            # Un seul modèle
            pred = list(predictions.values())[0]
            if 'probabilities' in pred and pred['probabilities']:
                home_prob = pred['probabilities'][0] * 100
                draw_prob = pred['probabilities'][1] * 100
                away_prob = pred['probabilities'][2] * 100
            else:
                return self._fallback_prediction(match_data)
        
        # Déterminer la prédiction
        probs = {'Home': home_prob, 'Draw': draw_prob, 'Away': away_prob}
        best_prediction = max(probs, key=probs.get)
        
        return {
            'prediction': match_data.get("home_team", "Home") if best_prediction == 'Home' else (
                "Draw" if best_prediction == 'Draw' else match_data.get("away_team", "Away")
            ),
            'home_win_pct': round(home_prob, 1),
            'draw_pct': round(draw_prob, 1),
            'away_win_pct': round(away_prob, 1),
            'confidence': round(max(home_prob, draw_prob, away_prob), 1)
        }
    
    def _fallback_prediction(self, match_data: Dict) -> Dict:
        """Prédiction de secours basée sur les odds."""
        home_odds = match_data.get("home_odds", 2.0)
        away_odds = match_data.get("away_odds", 3.0)
        draw_odds = match_data.get("draw_odds", 3.2)
        
        total = 1/home_odds + 1/away_odds + 1/draw_odds
        home_prob = (1/home_odds) / total * 100
        draw_prob = (1/draw_odds) / total * 100
        away_prob = (1/away_odds) / total * 100
        
        probs = {'Home': home_prob, 'Draw': draw_prob, 'Away': away_prob}
        best_prediction = max(probs, key=probs.get)
        
        return {
            'prediction': match_data.get("home_team", "Home") if best_prediction == 'Home' else (
                "Draw" if best_prediction == 'Draw' else match_data.get("away_team", "Away")
            ),
            'home_win_pct': round(home_prob, 1),
            'draw_pct': round(draw_prob, 1),
            'away_win_pct': round(away_prob, 1),
            'confidence': round(max(home_prob, draw_prob, away_prob), 1)
        }
    
    def predict_multiple_matches(self, matches: List[Dict]) -> List[Dict]:
        """Prédit plusieurs matchs."""
        predictions = []
        for match in matches:
            pred = self.predict_match(match)
            match_result = {**match, **pred}
            predictions.append(match_result)
        return predictions


# Instance globale du service
_service: Optional[PredictionService] = None


def get_prediction_service() -> PredictionService:
    """Obtient ou crée l'instance du service de prédiction."""
    global _service
    if _service is None:
        _service = PredictionService()
    return _service


def predict_match(match_data: Dict) -> Dict:
    """Prédit un match."""
    service = get_prediction_service()
    return service.predict_match(match_data)


def predict_matches(matches: List[Dict]) -> List[Dict]:
    """Prédit plusieurs matchs."""
    service = get_prediction_service()
    return service.predict_multiple_matches(matches)

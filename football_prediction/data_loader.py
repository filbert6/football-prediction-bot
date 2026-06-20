"""Module pour charger les données réelles et générer les matchs."""
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"


class DataLoader:
    """Charge les données réelles des matches."""
    
    def __init__(self):
        self.matches_cache = None
        self.history_cache = None
        self.stats_cache = None
    
    def load_upcoming_matches(self) -> List[Dict]:
        """Charge les matches à venir."""
        try:
            # Chercher les données CSV si disponibles
            processed_files = list(PROCESSED_DIR.glob("*.csv"))
            
            if processed_files:
                for file in processed_files:
                    try:
                        df = pd.read_csv(file)
                        if 'date' in df.columns or 'Date' in df.columns:
                            # Supposer que ce sont les matches à venir
                            return self._convert_df_to_matches(df)
                    except Exception as e:
                        logger.warning(f"Impossible de lire {file}: {e}")
            
            # Sinon, générer des données de démonstration réalistes
            return self._generate_demo_matches()
        except Exception as e:
            logger.exception(f"Erreur lors du chargement des matches: {e}")
            return self._generate_demo_matches()
    
    def load_match_history(self) -> List[Dict]:
        """Charge l'historique des matches."""
        try:
            # Chercher les données historiques
            processed_files = list(PROCESSED_DIR.glob("*history*.csv"))
            
            if processed_files:
                for file in processed_files:
                    try:
                        df = pd.read_csv(file)
                        return self._convert_df_to_history(df)
                    except Exception as e:
                        logger.warning(f"Impossible de lire {file}: {e}")
            
            return self._generate_demo_history()
        except Exception as e:
            logger.exception(f"Erreur lors du chargement de l'historique: {e}")
            return self._generate_demo_history()
    
    def load_statistics(self) -> Dict:
        """Charge les statistiques globales."""
        try:
            stats_file = PROCESSED_DIR / "statistics.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    return json.load(f)
            
            return self._calculate_statistics()
        except Exception as e:
            logger.exception(f"Erreur lors du chargement des statistiques: {e}")
            return self._calculate_statistics()
    
    def _generate_demo_matches(self) -> List[Dict]:
        """Génère des matches de démonstration réalistes."""
        today = datetime.now().date()
        
        matches_data = [
            {
                "date": today + timedelta(days=1),
                "league": "Ligue 1",
                "home_team": "Paris SG",
                "away_team": "Marseille",
                "home_odds": 1.85,
                "draw_odds": 3.50,
                "away_odds": 4.20,
                "home_elo": 1850,
                "away_elo": 1620,
                "home_form": 0.72,
                "away_form": 0.58,
                "home_attack": 0.78,
                "away_attack": 0.65,
                "home_defense": 0.82,
                "away_defense": 0.68,
            },
            {
                "date": today + timedelta(days=2),
                "league": "Premier League",
                "home_team": "Manchester City",
                "away_team": "Liverpool",
                "home_odds": 2.15,
                "draw_odds": 3.40,
                "away_odds": 3.30,
                "home_elo": 1820,
                "away_elo": 1800,
                "home_form": 0.70,
                "away_form": 0.68,
                "home_attack": 0.81,
                "away_attack": 0.79,
                "home_defense": 0.80,
                "away_defense": 0.78,
            },
            {
                "date": today + timedelta(days=2),
                "league": "La Liga",
                "home_team": "Real Madrid",
                "away_team": "Barcelona",
                "home_odds": 2.40,
                "draw_odds": 3.20,
                "away_odds": 2.95,
                "home_elo": 1810,
                "away_elo": 1780,
                "home_form": 0.71,
                "away_form": 0.69,
                "home_attack": 0.79,
                "away_attack": 0.77,
                "home_defense": 0.81,
                "away_defense": 0.79,
            },
            {
                "date": today + timedelta(days=3),
                "league": "Serie A",
                "home_team": "Juventus",
                "away_team": "Inter Milan",
                "home_odds": 2.35,
                "draw_odds": 3.30,
                "away_odds": 3.10,
                "home_elo": 1790,
                "away_elo": 1770,
                "home_form": 0.68,
                "away_form": 0.67,
                "home_attack": 0.75,
                "away_attack": 0.74,
                "home_defense": 0.79,
                "away_defense": 0.78,
            },
            {
                "date": today + timedelta(days=3),
                "league": "Bundesliga",
                "home_team": "Bayern Munich",
                "away_team": "Borussia Dortmund",
                "home_odds": 1.95,
                "draw_odds": 3.50,
                "away_odds": 3.80,
                "home_elo": 1830,
                "away_elo": 1710,
                "home_form": 0.74,
                "away_form": 0.61,
                "home_attack": 0.82,
                "away_attack": 0.68,
                "home_defense": 0.84,
                "away_defense": 0.71,
            },
        ]
        
        return matches_data
    
    def _generate_demo_history(self) -> List[Dict]:
        """Génère un historique de démonstration."""
        today = datetime.now().date()
        
        history = [
            {
                "date": today - timedelta(days=1),
                "home_team": "Paris SG",
                "away_team": "Nantes",
                "score": "3-1",
                "prediction": "Paris SG",
                "result": "Correct",
                "confidence": 87,
            },
            {
                "date": today - timedelta(days=3),
                "home_team": "Manchester City",
                "away_team": "Fulham",
                "score": "4-1",
                "prediction": "Manchester City",
                "result": "Correct",
                "confidence": 91,
            },
            {
                "date": today - timedelta(days=5),
                "home_team": "Real Madrid",
                "away_team": "Almeria",
                "score": "2-2",
                "prediction": "Real Madrid",
                "result": "Partial",
                "confidence": 74,
            },
            {
                "date": today - timedelta(days=7),
                "home_team": "Juventus",
                "away_team": "Roma",
                "score": "1-0",
                "prediction": "Juventus",
                "result": "Correct",
                "confidence": 78,
            },
            {
                "date": today - timedelta(days=9),
                "home_team": "Bayern Munich",
                "away_team": "Augsburg",
                "score": "3-0",
                "prediction": "Bayern Munich",
                "result": "Correct",
                "confidence": 89,
            },
        ]
        
        return history
    
    def _calculate_statistics(self) -> Dict:
        """Calcule les statistiques globales."""
        history = self.load_match_history()
        
        correct = sum(1 for h in history if h.get("result") == "Correct")
        partial = sum(1 for h in history if h.get("result") == "Partial")
        total = len(history)
        
        accuracy = (correct + partial * 0.5) / total * 100 if total > 0 else 0
        
        return {
            "total_predictions": total,
            "correct_predictions": correct,
            "accuracy": round(accuracy, 1),
            "models_active": 1,
            "last_update": datetime.now().isoformat(),
        }
    
    def _convert_df_to_matches(self, df: pd.DataFrame) -> List[Dict]:
        """Convertit un DataFrame en liste de matches."""
        matches = []
        for _, row in df.iterrows():
            match = {
                "date": pd.to_datetime(row.get("date", row.get("Date"))).date(),
                "league": row.get("league", row.get("League", "Unknown")),
                "home_team": row.get("home_team", row.get("Home Team", "Home")),
                "away_team": row.get("away_team", row.get("Away Team", "Away")),
                "home_odds": float(row.get("home_odds", row.get("Home Odds", 2.0))),
                "draw_odds": float(row.get("draw_odds", row.get("Draw Odds", 3.2))),
                "away_odds": float(row.get("away_odds", row.get("Away Odds", 3.0))),
                "home_elo": float(row.get("home_elo", 1600)),
                "away_elo": float(row.get("away_elo", 1600)),
                "home_form": float(row.get("home_form", 0.5)),
                "away_form": float(row.get("away_form", 0.5)),
                "home_attack": float(row.get("home_attack", 0.5)),
                "away_attack": float(row.get("away_attack", 0.5)),
                "home_defense": float(row.get("home_defense", 0.5)),
                "away_defense": float(row.get("away_defense", 0.5)),
            }
            matches.append(match)
        
        return matches
    
    def _convert_df_to_history(self, df: pd.DataFrame) -> List[Dict]:
        """Convertit un DataFrame en historique."""
        history = []
        for _, row in df.iterrows():
            item = {
                "date": pd.to_datetime(row.get("date", row.get("Date"))).date(),
                "home_team": row.get("home_team", row.get("Home Team", "Home")),
                "away_team": row.get("away_team", row.get("Away Team", "Away")),
                "score": row.get("score", row.get("Score", "-")),
                "prediction": row.get("prediction", row.get("Prediction", "-")),
                "result": row.get("result", row.get("Result", "Unknown")),
                "confidence": int(row.get("confidence", row.get("Confidence", 50))),
            }
            history.append(item)
        
        return history


# Instance globale
_loader: DataLoader = None


def get_data_loader() -> DataLoader:
    """Obtient l'instance du loader de données."""
    global _loader
    if _loader is None:
        _loader = DataLoader()
    return _loader


def load_upcoming_matches() -> List[Dict]:
    """Charge les matches à venir."""
    loader = get_data_loader()
    return loader.load_upcoming_matches()


def load_match_history() -> List[Dict]:
    """Charge l'historique des matches."""
    loader = get_data_loader()
    return loader.load_match_history()


def load_statistics() -> Dict:
    """Charge les statistiques."""
    loader = get_data_loader()
    return loader.load_statistics()

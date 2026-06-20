"""Module pour charger les données réelles et générer les matchs."""
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

import pandas as pd

try:
    from .config_loader import load_config, get_competitions
except ImportError:
    from config_loader import load_config, get_competitions

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
        self.config = load_config()
        self.competitions = get_competitions(self.config)

    def load_upcoming_matches(self) -> List[Dict[str, Any]]:
        """Charge les matches à venir."""
        try:
            processed_files = list(PROCESSED_DIR.rglob("*.csv"))
            upcoming_matches: List[Dict[str, Any]] = []

            for file in processed_files:
                file_name = file.name.lower()
                if any(skip in file_name for skip in ["history", "statistics", "predictions"]):
                    continue

                try:
                    df = pd.read_csv(file, low_memory=False)
                    df = self._normalize_dataframe(df)
                    df = self._filter_upcoming(df)
                    if not df.empty:
                        upcoming_matches.extend(self._convert_df_to_matches(df))
                except Exception as e:
                    logger.warning("Impossible de lire ou normaliser %s: %s", file, e)

            if upcoming_matches:
                return upcoming_matches

            return self._generate_demo_matches()
        except Exception as e:
            logger.exception("Erreur lors du chargement des matches: %s", e)
            return self._generate_demo_matches()

    def load_match_history(self) -> List[Dict[str, Any]]:
        """Charge l'historique des matches."""
        try:
            processed_files = list(PROCESSED_DIR.rglob("*history*.csv"))

            history: List[Dict[str, Any]] = []
            for file in processed_files:
                try:
                    df = pd.read_csv(file, low_memory=False)
                    history.extend(self._convert_df_to_history(df))
                except Exception as e:
                    logger.warning("Impossible de lire l'historique %s: %s", file, e)

            if history:
                return history

            return self._generate_demo_history()
        except Exception as e:
            logger.exception("Erreur lors du chargement de l'historique: %s", e)
            return self._generate_demo_history()

    def load_statistics(self) -> Dict[str, Any]:
        """Charge les statistiques globales."""
        try:
            stats_file = PROCESSED_DIR / "statistics.json"
            if stats_file.exists():
                with open(stats_file, "r", encoding="utf-8") as f:
                    return json.load(f)

            return self._calculate_statistics()
        except Exception as e:
            logger.exception("Erreur lors du chargement des statistiques: %s", e)
            return self._calculate_statistics()

    def _generate_demo_matches(self) -> List[Dict[str, Any]]:
        """Génère des matches de démonstration réalistes."""
        today = datetime.now().date()
        return [
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
        ]

    def _generate_demo_history(self) -> List[Dict[str, Any]]:
        """Génère un historique de démonstration."""
        today = datetime.now().date()
        return [
            {
                "date": today - timedelta(days=1),
                "home_team": "Paris SG",
                "away_team": "Nantes",
                "score": "3-1",
                "prediction": "Paris SG",
                "result": "Correct",
                "confidence": 87,
            }
        ]

    def _calculate_statistics(self) -> Dict[str, Any]:
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

    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.copy()
        columns = {col.lower().strip(): col for col in df.columns}
        column_map = {
            "date": ["date", "match_date", "kickoff", "kickoff_date"],
            "home_team": ["home_team", "hometeam", "home team", "home"],
            "away_team": ["away_team", "awayteam", "away team", "away"],
            "league": ["league", "competition", "tournament", "div", "division"],
            "home_odds": ["home_odds", "odds_home", "b365h", "psh", "1"],
            "draw_odds": ["draw_odds", "odds_draw", "b365d", "psd", "x"],
            "away_odds": ["away_odds", "odds_away", "b365a", "psa", "2"],
            "score": ["score", "ftr", "full_time_result"],
            "result": ["result", "match_result"],
            "confidence": ["confidence", "confidence_pct"],
        }

        rename_map = {}
        for target, candidates in column_map.items():
            for candidate in candidates:
                if candidate in columns:
                    rename_map[columns[candidate]] = target
                    break

        df = df.rename(columns=rename_map)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True).dt.date

        if "league" not in df.columns and "competition" in df.columns:
            df["league"] = df["competition"]

        if "league" not in df.columns:
            df["league"] = df.get("division") if "division" in df.columns else "Unknown"

        return df

    def _filter_upcoming(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty or "date" not in df.columns:
            return df
        today = datetime.now().date()
        upcoming = df[df["date"] >= today]
        return upcoming if not upcoming.empty else df

    def _convert_df_to_matches(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        matches = []
        for _, row in df.iterrows():
            match = {
                "date": pd.to_datetime(row.get("date")).date() if pd.notna(row.get("date")) else None,
                "league": row.get("league", row.get("competition", "Unknown")),
                "home_team": row.get("home_team", row.get("Home Team", "Home")),
                "away_team": row.get("away_team", row.get("Away Team", "Away")),
                "home_odds": float(row.get("home_odds", row.get("Home Odds", 2.0) or 2.0)),
                "draw_odds": float(row.get("draw_odds", row.get("Draw Odds", 3.2) or 3.2)),
                "away_odds": float(row.get("away_odds", row.get("Away Odds", 3.0) or 3.0)),
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

    def _convert_df_to_history(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        history = []
        for _, row in df.iterrows():
            item = {
                "date": pd.to_datetime(row.get("date", row.get("Date")), errors="coerce").date(),
                "home_team": row.get("home_team", row.get("Home Team", "Home")),
                "away_team": row.get("away_team", row.get("Away Team", "Away")),
                "score": row.get("score", row.get("Score", "-")),
                "prediction": row.get("prediction", row.get("Prediction", "-")),
                "result": row.get("result", row.get("Result", "Unknown")),
                "confidence": int(row.get("confidence", row.get("Confidence", 50))) if pd.notna(row.get("confidence", row.get("Confidence", 50))) else 50,
            }
            history.append(item)

        return history


_loader: DataLoader | None = None


def get_data_loader() -> DataLoader:
    global _loader
    if _loader is None:
        _loader = DataLoader()
    return _loader


def load_upcoming_matches() -> List[Dict[str, Any]]:
    loader = get_data_loader()
    return loader.load_upcoming_matches()


def load_match_history() -> List[Dict[str, Any]]:
    loader = get_data_loader()
    return loader.load_match_history()


def load_statistics() -> Dict[str, Any]:
    loader = get_data_loader()
    return loader.load_statistics()

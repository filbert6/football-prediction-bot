"""Calcul et extraction d'un rating Elo simple à partir de l'historique des matchs."""
import logging
from typing import Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def _ensure_date(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    if date_col in df.columns and not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    return df


def compute_elo_ratings(history: pd.DataFrame, k: int = 20, initial: int = 1600, home_adv: int = 100) -> Dict[str, int]:
    """Calcule les ratings Elo finaux pour toutes les équipes.

    history doit contenir: date, home_team, away_team, home_goals (ou home_score), away_goals (ou away_score).
    """
    history = _ensure_date(history)
    df = history.sort_values("date").copy()

    ratings: Dict[str, float] = {}

    def _get_score(hg, ag):
        if hg > ag:
            return 1.0, 0.0
        if hg < ag:
            return 0.0, 1.0
        return 0.5, 0.5

    for _, row in df.iterrows():
        home = row.get("home_team")
        away = row.get("away_team")
        hg = row.get("home_goals") if "home_goals" in row else row.get("home_score") or row.get("home_score")
        ag = row.get("away_goals") if "away_goals" in row else row.get("away_score") or row.get("away_score")

        try:
            if hg is None or ag is None:
                if "score" in row and isinstance(row.get("score"), str):
                    parts = row.get("score").split("-")
                    hg = int(parts[0]); ag = int(parts[1])
        except Exception:
            logger.debug("Impossible d'analyser le score pour la ligne: %s", row)
            continue

        if home is None or away is None or hg is None or ag is None:
            continue

        r_home = ratings.get(home, initial)
        r_away = ratings.get(away, initial)

        # expected
        exp_home = 1.0 / (1.0 + 10 ** (((r_away - r_home) - home_adv) / 400.0))
        exp_away = 1.0 / (1.0 + 10 ** (((r_home - r_away) + home_adv) / 400.0))

        s_home, s_away = _get_score(hg, ag)

        r_home_new = r_home + k * (s_home - exp_home)
        r_away_new = r_away + k * (s_away - exp_away)

        ratings[home] = r_home_new
        ratings[away] = r_away_new

    # round final ratings to ints
    return {team: int(round(r)) for team, r in ratings.items()}


def add_elo_features(upcoming: pd.DataFrame, history: pd.DataFrame, k: int = 20, initial: int = 1600) -> pd.DataFrame:
    """Ajoute `home_elo` et `away_elo` aux matchs à venir, calculés à partir de l'historique."""
    out = upcoming.copy()
    out = _ensure_date(out)
    history = _ensure_date(history)

    home_elos = []
    away_elos = []

    for _, row in out.iterrows():
        as_of = row.get("date")
        # ratings up to date
        past = history[history["date"] < pd.to_datetime(as_of)].sort_values("date")
        ratings = compute_elo_ratings(past, k=k, initial=initial)

        home = row.get("home_team")
        away = row.get("away_team")
        home_elos.append(ratings.get(home, initial))
        away_elos.append(ratings.get(away, initial))

    out["home_elo"] = home_elos
    out["away_elo"] = away_elos
    return out

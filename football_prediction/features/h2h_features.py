"""Extraction des statistiques Head-to-Head (H2H) pour un duo d'équipes."""
import logging
from typing import Tuple
import pandas as pd

logger = logging.getLogger(__name__)


def _ensure_date(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    if date_col in df.columns and not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    return df


def compute_h2h(home: str, away: str, history: pd.DataFrame, as_of=None, n: int = 10) -> Tuple[float, float]:
    """Calcule la force H2H pour `home` et `away` basée sur les n dernières confrontations.

    Retourne (home_h2h, away_h2h) où chaque valeur est dans [0,1] (win ratio pondéré par les n matchs).
    Les matchs nuls comptent pour 0.5 pour les deux équipes.
    """
    history = _ensure_date(history)
    df = history.copy()
    if as_of is not None:
        df = df[df["date"] < pd.to_datetime(as_of)]

    mask = ((df.get("home_team") == home) & (df.get("away_team") == away)) | (
        (df.get("home_team") == away) & (df.get("away_team") == home)
    )
    h2h = df[mask].sort_values("date", ascending=False).head(n)
    if h2h.empty:
        return 0.5, 0.5

    home_points = 0.0
    away_points = 0.0
    total = 0
    for _, row in h2h.iterrows():
        total += 1
        try:
            hg = row.get("home_goals") if "home_goals" in row else row.get("home_score")
            ag = row.get("away_goals") if "away_goals" in row else row.get("away_score")
            if hg is None or ag is None:
                if "score" in row and isinstance(row.get("score"), str):
                    parts = row.get("score").split("-")
                    hg = int(parts[0]); ag = int(parts[1])
        except Exception:
            hg = ag = None

        if hg is None or ag is None:
            total -= 1
            continue

        # qui était à domicile
        hteam = row.get("home_team")
        ateam = row.get("away_team")

        if hg > ag:
            if hteam == home:
                home_points += 1
            else:
                away_points += 1
        elif hg < ag:
            if ateam == home:
                home_points += 1
            else:
                away_points += 1
        else:
            # draw
            home_points += 0.5
            away_points += 0.5

    if total <= 0:
        return 0.5, 0.5

    return home_points / total, away_points / total


def add_h2h_features(upcoming: pd.DataFrame, history: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    out = upcoming.copy()
    out = _ensure_date(out)
    history = _ensure_date(history)

    home_h2h = []
    away_h2h = []
    for _, row in out.iterrows():
        as_of = row.get("date")
        home = row.get("home_team")
        away = row.get("away_team")
        h, a = compute_h2h(home, away, history, as_of=as_of, n=n)
        home_h2h.append(h)
        away_h2h.append(a)

    out["home_h2h"] = home_h2h
    out["away_h2h"] = away_h2h
    return out

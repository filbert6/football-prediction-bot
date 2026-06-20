"""Calcul des features de forme et xG/xGA."""
import logging
from typing import Optional
from pathlib import Path
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def _ensure_date(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    if date_col in df.columns and not np.issubdtype(df[date_col].dtype, np.datetime64):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    return df


def _find_xg_cols(df: pd.DataFrame):
    # Possible names for xG columns (home/away)
    candidates = [
        ("home_xg", "away_xg"),
        ("xg_home", "xg_away"),
        ("xg_h", "xg_a"),
        ("home_xG", "away_xG"),
    ]
    for h, a in candidates:
        if h in df.columns and a in df.columns:
            return h, a
    return None, None


def compute_form(team: str, history: pd.DataFrame, as_of=None, n: int = 5) -> float:
    """Calcule le ratio de victoires sur les n derniers matchs avant `as_of`.

    Retourne une valeur entre 0 et 1. Si pas assez de matchs, calcule sur ceux disponibles.
    """
    history = _ensure_date(history)
    df = history.copy()
    if as_of is not None:
        df = df[df["date"] < pd.to_datetime(as_of)]

    # sélectionner les matchs du team en tant que maison ou extérieur
    mask = (df.get("home_team") == team) | (df.get("away_team") == team)
    team_matches = df[mask].sort_values("date", ascending=False).head(n)
    if team_matches.empty:
        return 0.5

    wins = 0
    total = 0
    for _, row in team_matches.iterrows():
        total += 1
        try:
            home = row.get("home_team")
            away = row.get("away_team")
            hg = row.get("home_goals") if "home_goals" in row else row.get("home_score") or row.get("home_score")
            ag = row.get("away_goals") if "away_goals" in row else row.get("away_score") or row.get("away_score")
            # fallback parsing from 'score' column like '2-1'
            if (hg is None or ag is None) and "score" in row and isinstance(row.get("score"), str):
                try:
                    parts = row.get("score").split("-")
                    hg = int(parts[0])
                    ag = int(parts[1])
                except Exception:
                    hg = ag = None
        except Exception:
            hg = ag = None

        if hg is None or ag is None:
            # cannot determine result -> assume draw neutral
            total -= 1
            continue

        if team == home and hg > ag:
            wins += 1
        elif team == away and ag > hg:
            wins += 1

    if total <= 0:
        return 0.5
    return wins / total


def compute_xg(team: str, history: pd.DataFrame, as_of=None, n: int = 5) -> float:
    """Calcule le xG moyen du `team` sur les n derniers matchs avant `as_of`.

    Recherche automatiquement les colonnes xG/ xGA.
    """
    history = _ensure_date(history)
    df = history.copy()
    if as_of is not None:
        df = df[df["date"] < pd.to_datetime(as_of)]

    hcol, acol = _find_xg_cols(df)
    if hcol is None:
        logger.debug("Aucune colonne xG détectée dans l'historique")
        return 0.0

    mask = (df.get("home_team") == team) | (df.get("away_team") == team)
    team_matches = df[mask].sort_values("date", ascending=False).head(n)
    if team_matches.empty:
        return 0.0

    vals = []
    for _, row in team_matches.iterrows():
        if row.get("home_team") == team:
            vals.append(row.get(hcol, np.nan))
        else:
            vals.append(row.get(acol, np.nan))

    vals = [v for v in vals if pd.notna(v)]
    if not vals:
        return 0.0
    return float(np.mean(vals))


def compute_xga(team: str, history: pd.DataFrame, as_of=None, n: int = 5) -> float:
    """Calcule le xGA moyen du `team` sur les n derniers matchs avant `as_of`."""
    history = _ensure_date(history)
    df = history.copy()
    if as_of is not None:
        df = df[df["date"] < pd.to_datetime(as_of)]

    hcol, acol = _find_xg_cols(df)
    if hcol is None:
        return 0.0

    mask = (df.get("home_team") == team) | (df.get("away_team") == team)
    team_matches = df[mask].sort_values("date", ascending=False).head(n)
    if team_matches.empty:
        return 0.0

    vals = []
    for _, row in team_matches.iterrows():
        if row.get("home_team") == team:
            vals.append(row.get(acol, np.nan))
        else:
            vals.append(row.get(hcol, np.nan))

    vals = [v for v in vals if pd.notna(v)]
    if not vals:
        return 0.0
    return float(np.mean(vals))


def add_form_xg_features(upcoming: pd.DataFrame, history: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Ajoute les colonnes home_form, away_form, home_xg, away_xg, home_xga, away_xga."""
    out = upcoming.copy()
    out = _ensure_date(out)
    history = _ensure_date(history)

    home_forms = []
    away_forms = []
    home_xgs = []
    away_xgs = []
    home_xgas = []
    away_xgas = []

    for _, row in out.iterrows():
        as_of = row.get("date")
        home = row.get("home_team")
        away = row.get("away_team")

        home_forms.append(compute_form(home, history, as_of=as_of, n=n))
        away_forms.append(compute_form(away, history, as_of=as_of, n=n))

        home_xgs.append(compute_xg(home, history, as_of=as_of, n=n))
        away_xgs.append(compute_xg(away, history, as_of=as_of, n=n))

        home_xgas.append(compute_xga(home, history, as_of=as_of, n=n))
        away_xgas.append(compute_xga(away, history, as_of=as_of, n=n))

    out["home_form"] = home_forms
    out["away_form"] = away_forms
    out["home_xg"] = home_xgs
    out["away_xg"] = away_xgs
    out["home_xga"] = home_xgas
    out["away_xga"] = away_xgas

    return out

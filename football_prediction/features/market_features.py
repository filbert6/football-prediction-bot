"""Extraction des cotes bookmakers et probabilités implicites."""
import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def _find_odds_cols(df: pd.DataFrame):
    candidates = [
        ("home_odds", "draw_odds", "away_odds"),
        ("odds_home", "odds_draw", "odds_away"),
        ("h_odds", "d_odds", "a_odds"),
    ]
    for cols in candidates:
        if all(c in df.columns for c in cols):
            return cols
    return None


def implied_prob_from_odds(odds: float) -> Optional[float]:
    try:
        if odds <= 0 or pd.isna(odds):
            return None
        return 1.0 / float(odds)
    except Exception:
        return None


def add_market_features(upcoming: pd.DataFrame, odds_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Ajoute `home_odds`, `draw_odds`, `away_odds` et probabilités implicites si possible.

    Si `upcoming` contient déjà les cotes, les conserve. Sinon si `odds_df` fourni, tente de faire un match approximate.
    """
    out = upcoming.copy()

    if "home_odds" in out.columns and "away_odds" in out.columns and "draw_odds" in out.columns:
        # compute implied probs
        out["home_prob_imp"] = out["home_odds"].apply(lambda x: implied_prob_from_odds(x))
        out["draw_prob_imp"] = out["draw_odds"].apply(lambda x: implied_prob_from_odds(x))
        out["away_prob_imp"] = out["away_odds"].apply(lambda x: implied_prob_from_odds(x))
        # normalise
        s = out["home_prob_imp"] + out["draw_prob_imp"] + out["away_prob_imp"]
        out["home_prob_imp"] = (out["home_prob_imp"] / s).fillna(0)
        out["draw_prob_imp"] = (out["draw_prob_imp"] / s).fillna(0)
        out["away_prob_imp"] = (out["away_prob_imp"] / s).fillna(0)
        return out

    if odds_df is None:
        logger.info("Aucune DataFrame de cotes fournie et pas de colonnes existantes dans 'upcoming'")
        out["home_odds"] = None
        out["draw_odds"] = None
        out["away_odds"] = None
        out["home_prob_imp"] = None
        out["draw_prob_imp"] = None
        out["away_prob_imp"] = None
        return out

    # try to match by league/date/home/away
    odds_df = odds_df.copy()
    odds_df["home_team_norm"] = odds_df["home_team"].str.lower().str.strip()
    odds_df["away_team_norm"] = odds_df["away_team"].str.lower().str.strip()

    rows = []
    for _, row in out.iterrows():
        date = row.get("date")
        home = str(row.get("home_team") or "").lower().strip()
        away = str(row.get("away_team") or "").lower().strip()

        candidates = odds_df[(odds_df["home_team_norm"] == home) & (odds_df["away_team_norm"] == away)]
        if not candidates.empty:
            o = candidates.iloc[0]
            home_odds = o.get("home_odds") or o.get("odds_home")
            draw_odds = o.get("draw_odds") or o.get("odds_draw")
            away_odds = o.get("away_odds") or o.get("odds_away")
        else:
            home_odds = draw_odds = away_odds = None

        rows.append((home_odds, draw_odds, away_odds))

    out["home_odds"] = [r[0] for r in rows]
    out["draw_odds"] = [r[1] for r in rows]
    out["away_odds"] = [r[2] for r in rows]

    out["home_prob_imp"] = out["home_odds"].apply(lambda x: implied_prob_from_odds(x))
    out["draw_prob_imp"] = out["draw_odds"].apply(lambda x: implied_prob_from_odds(x))
    out["away_prob_imp"] = out["away_odds"].apply(lambda x: implied_prob_from_odds(x))
    s = out["home_prob_imp"] + out["draw_prob_imp"] + out["away_prob_imp"]
    out["home_prob_imp"] = (out["home_prob_imp"] / s).fillna(0)
    out["draw_prob_imp"] = (out["draw_prob_imp"] / s).fillna(0)
    out["away_prob_imp"] = (out["away_prob_imp"] / s).fillna(0)

    return out

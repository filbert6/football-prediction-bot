import logging
import os
from pathlib import Path
from typing import List, Optional

import pandas as pd
from soccerdata.fbref import FBref

try:
    from .config_loader import get_data_sources, load_config
except ImportError:
    from config_loader import get_data_sources, load_config

logger = logging.getLogger(__name__)
SOURCE_NAME = "fbref"
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def _make_list(value: Optional[str] | List[str]) -> Optional[List[str]]:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if item is not None]
    values = [item.strip() for item in str(value).split(",") if item.strip()]
    return values or None


def _parse_seasons(value: Optional[str] | List[int]) -> Optional[List[int]]:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [int(item) for item in value if item is not None]
    seasons = []
    for item in [piece.strip() for piece in str(value).split(",") if piece.strip()]:
        try:
            seasons.append(int(item))
        except ValueError:
            logger.warning("Skipping invalid FBref season value: %s", item)
    return seasons or None


def _save_dataframe(df: pd.DataFrame, filename: str, directory: Path) -> Path:
    path = directory / filename
    df.to_csv(path, index=False)
    logger.info("Saved %s rows to %s", len(df), path)
    return path


def _normalize_schedule(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    lower_columns = {col.lower().strip(): col for col in df.columns}
    rename_map = {}
    synonyms = {
        "date": ["date", "match_date", "kickoff", "kickoff_date"],
        "home_team": ["home_team", "hometeam", "home team", "home"],
        "away_team": ["away_team", "awayteam", "away team", "away"],
        "league": ["league", "competition", "tournament", "div"],
        "home_odds": ["home_odds", "odds_home", "b365h", "psh", "1"],
        "draw_odds": ["draw_odds", "odds_draw", "b365d", "psd", "x"],
        "away_odds": ["away_odds", "odds_away", "b365a", "psa", "2"],
    }

    for target, keys in synonyms.items():
        for source_key in keys:
            if source_key in lower_columns:
                rename_map[lower_columns[source_key]] = target
                break

    df = df.rename(columns=rename_map)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True).dt.date

    league_column = df.get("league")
    if league_column is None:
        league_column = df.get("competition") or df.get("tournament")
        if league_column is not None:
            df["league"] = league_column

    df["league"] = df["league"].fillna("FBref")
    df["source"] = "fbref"

    return df[[col for col in ["date", "league", "home_team", "away_team", "home_odds", "draw_odds", "away_odds", "source"] if col in df.columns]]


def _get_source_config() -> dict:
    config = load_config()
    return get_data_sources(config).get("fbref", {})


def run() -> bool:
    source_config = _get_source_config()
    if not source_config.get("enabled", True):
        logger.info("FBref scraper disabled in configuration")
        return False

    leagues = _make_list(os.environ.get("FBREF_LEAGUES") or source_config.get("leagues"))
    seasons = _parse_seasons(os.environ.get("FBREF_SEASONS") or source_config.get("seasons"))
    headless = source_config.get("headless", True)

    if leagues == ["all"]:
        leagues = None

    logger.info("Starting FBref scraper: leagues=%s seasons=%s", leagues, seasons)

    try:
        reader = FBref(
            leagues=leagues,
            seasons=seasons,
            headless=headless,
            no_cache=False,
            no_store=False,
            data_dir=RAW_DIR / "fbref_cache",
        )

        schedule = reader.read_schedule()
        if schedule is not None and not schedule.empty:
            normalized = _normalize_schedule(schedule)
            if not normalized.empty:
                _save_dataframe(normalized, "fbref_schedule.csv", PROCESSED_DIR)

        team_match_stats = reader.read_team_match_stats(force_cache=False)
        _save_dataframe(team_match_stats, "fbref_team_match_stats.csv", RAW_DIR)

        season_stats = reader.read_team_season_stats()
        _save_dataframe(season_stats, "fbref_team_season_stats.csv", RAW_DIR)

        leagues_df = reader.read_leagues()
        _save_dataframe(leagues_df, "fbref_leagues.csv", RAW_DIR)

        seasons_df = reader.read_seasons()
        _save_dataframe(seasons_df, "fbref_seasons.csv", RAW_DIR)

        logger.info("FBref scraper completed successfully")
        return True
    except Exception:
        logger.exception("FBref scraper encountered an error")
        return False

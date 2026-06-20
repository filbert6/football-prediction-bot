import logging
import os
from pathlib import Path
from typing import List, Optional

import pandas as pd
import requests

try:
    from .config_loader import get_data_sources, load_config
except ImportError:
    from config_loader import get_data_sources, load_config

logger = logging.getLogger(__name__)
SOURCE_NAME = "football_data_co_uk"
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def _download_csv(url: str, destination: Path) -> Path:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    destination.write_bytes(response.content)
    logger.info("Downloaded %s to %s", url, destination)
    return destination


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
        "league": ["league", "div", "division", "competition", "tournament"],
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

    df["league"] = df.get("league")
    if df["league"].isna().all() if "league" in df.columns else True:
        df["league"] = df.get("div") or df.get("division") or "Football-Data.co.uk"

    df["source"] = "football_data_co_uk"
    return df[[col for col in ["date", "league", "home_team", "away_team", "home_odds", "draw_odds", "away_odds", "source"] if col in df.columns]]


def _get_source_config() -> dict:
    config = load_config()
    return get_data_sources(config).get("football_data_co_uk", {})


def run() -> bool:
    source_config = _get_source_config()
    if not source_config.get("enabled", False):
        logger.info("Football-Data.co.uk scraper disabled in configuration")
        return False

    files: List[Path] = []
    raw_dir = RAW_DIR / "football_data_co_uk"
    raw_dir.mkdir(parents=True, exist_ok=True)

    for url in source_config.get("urls", []):
        try:
            target = raw_dir / Path(url).name
            files.append(_download_csv(url, target))
        except Exception as exc:
            logger.warning("Could not download football-data.co.uk URL %s: %s", url, exc)

    for file_name in source_config.get("files", []):
        candidate = Path(file_name)
        if not candidate.is_absolute():
            candidate = BASE_DIR / file_name
        if candidate.exists():
            files.append(candidate)
        else:
            logger.warning("Configured football-data.co.uk file not found: %s", candidate)

    if not files:
        logger.warning("No football-data.co.uk files or URLs configured")
        return False

    schedule = pd.DataFrame()
    for path in files:
        try:
            frame = pd.read_csv(path, low_memory=False)
            normalized = _normalize_schedule(frame)
            if not normalized.empty:
                schedule = pd.concat([schedule, normalized], ignore_index=True)
        except Exception as exc:
            logger.warning("Could not read football-data.co.uk file %s: %s", path, exc)

    if schedule.empty:
        logger.warning("No football-data.co.uk schedule data could be parsed")
        return False

    _save_dataframe(schedule.drop_duplicates(), "football_data_co_uk_schedule.csv", PROCESSED_DIR)
    logger.info("Football-Data.co.uk scraper completed successfully")
    return True

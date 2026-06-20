import os
from pathlib import Path
from typing import Any

import yaml

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_FILE = BASE_DIR / "config.yaml"
COMPETITIONS_FILE = BASE_DIR / "config" / "competitions.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(config_path: str | None = None) -> dict[str, Any]:
    path = Path(config_path or os.environ.get("FOOTBALL_PREDICTION_CONFIG") or DEFAULT_CONFIG_FILE)
    config = _load_yaml(path)

    # Merge optional competition metadata from a secondary YAML file.
    competitions = _load_yaml(COMPETITIONS_FILE).get("competitions", {})
    if competitions:
        config.setdefault("competitions", {}).update(competitions)

    return config


def get_data_sources(config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or load_config()
    return config.get("data_sources", {})


def get_competitions(config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    config = config or load_config()
    competitions = []
    for category, items in config.get("competitions", {}).items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    item = item.copy()
                    item["category"] = category
                    competitions.append(item)
    return competitions

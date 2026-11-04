from pathlib import Path
import json
import yaml


def load_yaml_config(file_path: Path) -> dict:
    """Load a YAML configuration file safely."""
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def save_yaml(file_path: Path, data: dict) -> None:
    """Save dictionary data to a YAML file, creating parent directories if needed."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False, allow_unicode=True)


def save_json(file_path: Path, data: dict) -> None:
    """Save dictionary data to a JSON file, creating parent directories if needed."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

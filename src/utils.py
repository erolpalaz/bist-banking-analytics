from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_project_root() -> Path:
    """Return project root path."""
    return PROJECT_ROOT


def load_json(path: str | Path) -> dict:
    """Load a JSON file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def ensure_directory(path: str | Path) -> Path:
    """Create directory if it does not exist and return Path object."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

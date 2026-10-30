"""Step 2: save / load the trusted baseline (JSON)."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

from .hasher import hash_folder

DEFAULT_BASELINE = Path("data/baseline.json")


class BaselineTamperedError(Exception):
    """Raised when the baseline file does not match its own checksum."""


def _checksum(folder: str, files: dict) -> str:
    canonical = json.dumps({"folder": folder, "files": files}, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def create_baseline(folder, baseline_path=DEFAULT_BASELINE) -> dict:
    baseline_path = Path(baseline_path)
    baseline_path.parent.mkdir(parents=True, exist_ok=True)

    files = hash_folder(folder)
    folder_abs = str(Path(folder).resolve())
    data = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "folder": folder_abs,
        "file_count": len(files),
        "files": files,
        "baseline_checksum": _checksum(folder_abs, files),
    }
    baseline_path.write_text(json.dumps(data, indent=2))
    return data


def load_baseline(baseline_path=DEFAULT_BASELINE) -> dict:
    baseline_path = Path(baseline_path)
    if not baseline_path.exists():
        raise FileNotFoundError("No baseline found. Create one first.")
    data = json.loads(baseline_path.read_text())
    expected = _checksum(data["folder"], data["files"])
    if expected != data.get("baseline_checksum"):
        raise BaselineTamperedError(
            "Baseline file was modified outside this tool! Do not trust it."
        )
    return data
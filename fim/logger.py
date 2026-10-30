"""Timestamped audit log (CSV)."""
import csv
from datetime import datetime
from pathlib import Path

DEFAULT_LOG = Path("data/audit_log.csv")
FIELDS = ["timestamp", "event", "file", "old_hash", "new_hash"]


def _write(rows, log_path):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not log_path.exists()
    with open(log_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        w.writerows(rows)


def log_event(event, file="-", old_hash="-", new_hash="-", log_path=DEFAULT_LOG):
    _write([{
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event": event, "file": file, "old_hash": old_hash, "new_hash": new_hash,
    }], log_path)


def log_scan_result(result: dict, log_path=DEFAULT_LOG):
    """Write one row per change (or one SCAN_CLEAN row)."""
    now = datetime.now().isoformat(timespec="seconds")
    rows = []
    for c in result["modified"]:
        rows.append({"timestamp": now, "event": "MODIFIED", "file": c["file"],
                     "old_hash": c["old_hash"], "new_hash": c["new_hash"]})
    for c in result["added"]:
        rows.append({"timestamp": now, "event": "ADDED", "file": c["file"],
                     "old_hash": "-", "new_hash": c["new_hash"]})
    for c in result["deleted"]:
        rows.append({"timestamp": now, "event": "DELETED", "file": c["file"],
                     "old_hash": c["old_hash"], "new_hash": "-"})
    if not rows:
        rows.append({"timestamp": now, "event": "SCAN_CLEAN", "file": "-",
                     "old_hash": "-", "new_hash": "-"})
    _write(rows, log_path)


def read_log(log_path=DEFAULT_LOG) -> list:
    log_path = Path(log_path)
    if not log_path.exists():
        return []
    with open(log_path, newline="") as f:
        return list(csv.DictReader(f))
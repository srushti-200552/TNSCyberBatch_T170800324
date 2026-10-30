"""Step 3: re-hash files and compare against the baseline."""
from .baseline import DEFAULT_BASELINE, load_baseline
from .hasher import hash_folder
from .logger import DEFAULT_LOG, log_scan_result


def compare(baseline_files: dict, current_files: dict) -> dict:
    modified, added, deleted, unchanged = [], [], [], []

    for name, old in baseline_files.items():
        if name not in current_files:
            deleted.append({"file": name, "old_hash": old["sha256"]})
        elif current_files[name]["sha256"] != old["sha256"]:
            modified.append({"file": name, "old_hash": old["sha256"],
                             "new_hash": current_files[name]["sha256"]})
        else:
            unchanged.append(name)

    for name, new in current_files.items():
        if name not in baseline_files:
            added.append({"file": name, "new_hash": new["sha256"]})

    return {"modified": modified, "added": added,
            "deleted": deleted, "unchanged": unchanged}


def scan(baseline_path=DEFAULT_BASELINE, log_path=DEFAULT_LOG, log=True) -> dict:
    baseline = load_baseline(baseline_path)       # also checks baseline tampering
    current = hash_folder(baseline["folder"])
    result = compare(baseline["files"], current)
    if log:
        log_scan_result(result, log_path)
    return result
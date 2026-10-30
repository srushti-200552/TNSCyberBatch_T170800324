"""Step 1: calculate SHA-256 hashes of files."""
import hashlib
from datetime import datetime
from pathlib import Path


def sha256_file(path, chunk_size: int = 65536) -> str:
    """Hash one file in chunks (works for large files too)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk_size), b""):
            h.update(block)
    return h.hexdigest()


def hash_folder(folder) -> dict:
    """Hash every file in a folder (recursively).

    Returns {relative_path: {"sha256": ..., "size": ..., "modified": ...}}
    """
    folder = Path(folder).resolve()
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")

    result = {}
    for p in sorted(folder.rglob("*")):
        if not p.is_file():
            continue
        try:
            info = p.stat()
            result[p.relative_to(folder).as_posix()] = {
                "sha256": sha256_file(p),
                "size": info.st_size,
                "modified": datetime.fromtimestamp(info.st_mtime).isoformat(timespec="seconds"),
            }
        except (PermissionError, OSError):
            continue  # skip unreadable files
    return result
"""OPTIONAL: real-time monitoring with watchdog."""
import time
from pathlib import Path

from .baseline import DEFAULT_BASELINE, load_baseline
from .hasher import sha256_file
from .logger import log_event


def watch(baseline_path=DEFAULT_BASELINE):
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    baseline = load_baseline(baseline_path)
    root = Path(baseline["folder"])
    known = baseline["files"]
    last_seen = {}

    def rel(p):
        try:
            return Path(p).resolve().relative_to(root).as_posix()
        except ValueError:
            return None

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory:
                return
            name = rel(event.src_path)
            if not name or name not in known:
                return
            try:
                new = sha256_file(event.src_path)
            except OSError:
                return
            if new != known[name]["sha256"] and last_seen.get(name) != new:
                last_seen[name] = new
                print(f"[MODIFIED] {name}")
                log_event("MODIFIED", name, known[name]["sha256"], new)

        def on_created(self, event):
            if event.is_directory:
                return
            name = rel(event.src_path)
            if name and name not in known:
                try:
                    new = sha256_file(event.src_path)
                except OSError:
                    return
                print(f"[ADDED] {name}")
                log_event("ADDED", name, "-", new)

        def on_deleted(self, event):
            if event.is_directory:
                return
            name = rel(event.src_path)
            if name and name in known:
                print(f"[DELETED] {name}")
                log_event("DELETED", name, known[name]["sha256"], "-")

    observer = Observer()
    observer.schedule(Handler(), str(root), recursive=True)
    observer.start()
    print(f"Watching {root} ... press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
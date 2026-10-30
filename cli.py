"""Command-line interface.

python cli.py demo-setup
python cli.py baseline sample_folder
python cli.py scan
python cli.py watch
"""
import argparse

from fim.baseline import BaselineTamperedError, create_baseline
from fim.demo import setup_demo
from fim.scanner import scan


def main():
    ap = argparse.ArgumentParser(description="File Integrity Monitor")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo-setup")
    b = sub.add_parser("baseline")
    b.add_argument("folder")
    sub.add_parser("scan")
    sub.add_parser("watch")
    args = ap.parse_args()

    if args.cmd == "demo-setup":
        setup_demo()
        print("Created sample_folder/")
    elif args.cmd == "baseline":
        data = create_baseline(args.folder)
        print(f"Baseline saved: {data['file_count']} files")
    elif args.cmd == "scan":
        try:
            r = scan()
        except BaselineTamperedError as e:
            print("ALERT:", e)
            return
        print(f"Modified: {len(r['modified'])} | Added: {len(r['added'])} | "
              f"Deleted: {len(r['deleted'])} | Unchanged: {len(r['unchanged'])}")
        for k in ("modified", "added", "deleted"):
            for c in r[k]:
                print(f"  [{k.upper()}] {c['file']}")
    elif args.cmd == "watch":
        from fim.watcher import watch
        watch()


if __name__ == "__main__":
    main()
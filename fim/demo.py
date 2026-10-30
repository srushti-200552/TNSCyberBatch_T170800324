"""Helpers to create a sample folder and simulate attacks/changes."""
from pathlib import Path

DEMO_FOLDER = Path("sample_folder")


def setup_demo(folder=DEMO_FOLDER):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "notes.txt").write_text("Project notes: original content.\n")
    (folder / "config.ini").write_text("[server]\nport=8080\nadmin=false\n")
    (folder / "report.txt").write_text("Quarterly report - confidential.\n")


def modify_demo_file(folder=DEMO_FOLDER):
    with open(Path(folder) / "notes.txt", "a") as f:
        f.write("TAMPERED: this line was added later.\n")


def add_demo_file(folder=DEMO_FOLDER):
    (Path(folder) / "suspicious.exe.txt").write_text("I was not here before.\n")


def delete_demo_file(folder=DEMO_FOLDER):
    p = Path(folder) / "report.txt"
    if p.exists():
        p.unlink()


def reset_demo(folder=DEMO_FOLDER):
    folder = Path(folder)
    if folder.exists():
        for p in folder.glob("*"):
            if p.is_file():
                p.unlink()
    setup_demo(folder)
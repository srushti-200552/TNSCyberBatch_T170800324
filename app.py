"""Streamlit frontend.  Run:  streamlit run app.py"""
from pathlib import Path

import pandas as pd
import streamlit as st

from fim.baseline import BaselineTamperedError, create_baseline, load_baseline
from fim.demo import (DEMO_FOLDER, add_demo_file, delete_demo_file,
                      modify_demo_file, reset_demo)
from fim.hasher import sha256_file
from fim.logger import read_log
from fim.scanner import scan

st.set_page_config(page_title="File Integrity Monitor", page_icon="🛡️", layout="wide")
st.title("🛡️ File Integrity Monitoring")
st.caption("Detect whether monitored files have changed since a trusted baseline.")

# ---------------- Sidebar: configuration ----------------
st.sidebar.header("Settings")
folder = st.sidebar.text_input("Folder to monitor", value=str(DEMO_FOLDER))

if st.sidebar.button("📸 Create / Reset Baseline", use_container_width=True):
    try:
        data = create_baseline(folder)
        st.sidebar.success(f"Baseline saved ({data['file_count']} files)")
        st.session_state.pop("result", None)
    except Exception as e:
        st.sidebar.error(str(e))

if st.sidebar.button("🔍 Run Integrity Scan", use_container_width=True, type="primary"):
    try:
        st.session_state["result"] = scan()
    except BaselineTamperedError as e:
        st.sidebar.error(f"🚨 {e}")
    except Exception as e:
        st.sidebar.error(str(e))

st.sidebar.markdown("---")
st.sidebar.info("A hash shows THAT a file changed, not WHO changed it. "
                "Protect the baseline and logs.")

tab_dash, tab_demo, tab_base, tab_log = st.tabs(
    ["📊 Scan Results", "🎬 Demo Lab", "📁 Baseline", "🧾 Audit Log"])

# ---------------- Tab 1: scan results ----------------
with tab_dash:
    result = st.session_state.get("result")
    if not result:
        st.info("Create a baseline, then click **Run Integrity Scan** in the sidebar.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("✅ Unchanged", len(result["unchanged"]))
        c2.metric("✏️ Modified", len(result["modified"]))
        c3.metric("➕ Added", len(result["added"]))
        c4.metric("❌ Deleted", len(result["deleted"]))

        if not (result["modified"] or result["added"] or result["deleted"]):
            st.success("All files match the baseline. No changes detected.")
        else:
            st.error("Integrity violation detected!")

        if result["modified"]:
            st.subheader("Modified files (before vs after hash)")
            st.dataframe(pd.DataFrame(result["modified"]), use_container_width=True)
        if result["added"]:
            st.subheader("Newly added files")
            st.dataframe(pd.DataFrame(result["added"]), use_container_width=True)
        if result["deleted"]:
            st.subheader("Missing / deleted files")
            st.dataframe(pd.DataFrame(result["deleted"]), use_container_width=True)

# ---------------- Tab 2: demo lab ----------------
with tab_demo:
    st.subheader("Demo: monitor a sample folder, edit a file, compare hashes")
    st.markdown("**Flow:** 1) Create sample files → 2) Create baseline (sidebar) → "
                "3) Simulate a change → 4) Run scan (sidebar).")
    d1, d2, d3, d4, d5 = st.columns(5)
    if d1.button("1️⃣ Create sample files"):
        reset_demo()
        st.success("Sample folder created / reset.")
    if d2.button("✏️ Edit notes.txt"):
        notes = DEMO_FOLDER / "notes.txt"
        before = sha256_file(notes) if notes.exists() else "n/a"
        modify_demo_file()
        after = sha256_file(notes)
        st.session_state["before_after"] = (before, after)
    if d3.button("➕ Add new file"):
        add_demo_file()
        st.warning("suspicious.exe.txt added.")
    if d4.button("❌ Delete report.txt"):
        delete_demo_file()
        st.warning("report.txt deleted.")
    if d5.button("↩️ Reset sample files"):
        reset_demo()
        st.success("Reset done. Re-create the baseline.")

    if "before_after" in st.session_state:
        b, a = st.session_state["before_after"]
        st.markdown("#### Before / After hash of notes.txt")
        st.code(f"BEFORE: {b}\nAFTER : {a}")
        st.error("Hashes differ → file content changed.")

    st.markdown("#### Current files in sample folder")
    if DEMO_FOLDER.exists():
        rows = [{"file": p.name, "sha256": sha256_file(p)}
                for p in sorted(DEMO_FOLDER.glob("*")) if p.is_file()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ---------------- Tab 3: baseline ----------------
with tab_base:
    try:
        base = load_baseline()
        st.write(f"**Folder:** `{base['folder']}`  |  **Created:** {base['created_at']}  "
                 f"|  **Files:** {base['file_count']}")
        st.dataframe(pd.DataFrame(
            [{"file": k, **v} for k, v in base["files"].items()]),
            use_container_width=True)
        st.caption(f"Baseline checksum: {base['baseline_checksum']}")
    except FileNotFoundError:
        st.info("No baseline yet.")
    except BaselineTamperedError as e:
        st.error(f"🚨 {e}")

# ---------------- Tab 4: audit log ----------------
with tab_log:
    log = read_log()
    if not log:
        st.info("No audit entries yet. Run a scan.")
    else:
        df = pd.DataFrame(log).iloc[::-1]
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇️ Download log (CSV)", df.to_csv(index=False),
                           "audit_log.csv", "text/csv")
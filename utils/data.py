# utils/data.py

import io
import json
import logging
import os
from datetime import datetime, date

import pandas as pd
import streamlit as st

from utils.constants import (
    AGENT_CAMPAIGN_MAP,
    ALL_DISPOSITIONS,
    CACHE_FILE,
    CACHE_RAW_FILE,
    CONTACTED_DISPOSITIONS,
    CSV_CAMPAIGN_MAP,
    NOT_CONTACTED_DISPOSITIONS,
    TEST_AGENT_NAMES,
)

logger = logging.getLogger(__name__)


# ── Disposition classifier ────────────────────────────────────────────────────

def classify_disposition(raw) -> str:
    if pd.isna(raw):
        return "Not Contactable"
    d = str(raw).strip()
    if not d or d in {"-NA-", "DISPOSITION ADDED BY SYSTEM"}:
        return "Not Contactable"
    if d.startswith("Follow up") or d.startswith("Followup"):
        return "Followup"
    if d.startswith("Information"):
        return "Information Shared"
    if d.startswith("Quote"):
        return "Quote Sent"
    if d.startswith("Junk"):
        return "Junk"
    if d.startswith("Lost"):
        return "Lost"
    if d.startswith("Non Contactable") or d.startswith("Number in DNC") or d.startswith("Redial"):
        return "Not Contactable"
    if d in ALL_DISPOSITIONS:
        return d
    return "Not Contactable"


# ── Duration parser ───────────────────────────────────────────────────────────

def parse_duration_seconds(val) -> float:
    """Convert HH:MM:SS string to seconds. Returns 0 for NaN or 00:00:00."""
    try:
        if pd.isna(val):
            return 0.0
        td = pd.to_timedelta(str(val).strip(), errors="coerce")
        if pd.isna(td):
            return 0.0
        secs = td.total_seconds()
        return secs if secs > 0 else 0.0
    except Exception:
        return 0.0


def format_duration(total_seconds: float) -> str:
    """Format seconds as Xh Ym or Ym Zs."""
    total_seconds = int(total_seconds)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    if h > 0:
        return f"{h}h {m}m"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


# ── CSV processing ────────────────────────────────────────────────────────────

def _find_column(col_map: dict, candidates: list):
    return next((col_map[k] for k in candidates if k in col_map), None)


def process_csv(file_bytes: bytes, filename: str):
    """
    Parse InTalk Call History CSV.
    Returns: (summary_df, raw_df, csv_date, warnings)

    raw_df columns: Agent, Disposition, Campaign, Date, DurationSecs
    summary_df columns: Agent, Campaign, Attempts, Contacted, NotContacted,
                        Contact%, TalkTimeSecs
    """
    buf = io.BytesIO(file_bytes)
    df = None

    for skip in [4, 5, 3, 0]:
        try:
            buf.seek(0)
            trial = pd.read_csv(buf, skiprows=skip, encoding="utf-8-sig",
                                on_bad_lines="skip", low_memory=False)
            col_lower = {c.lower().strip(): c for c in trial.columns}
            if any(k in col_lower for k in ["agent username", "agent name", "agent"]) \
               and any(k in col_lower for k in ["disposition", "call status", "status"]):
                df = trial
                break
        except Exception as exc:
            logger.debug("skiprows=%d failed: %s", skip, exc)

    if df is None:
        raise ValueError("Could not detect column headers. Upload the InTalk Call History CSV export.")

    col_lower = {c.lower().strip(): c for c in df.columns}

    agent_col = _find_column(col_lower, ["agent username", "agent name", "agent"])
    disp_col  = _find_column(col_lower, ["disposition", "call status", "status"])
    date_col  = _find_column(col_lower, ["date time", "datetime", "date", "time"])
    dur_col   = _find_column(col_lower, ["duration"])

    if not agent_col:
        raise ValueError(f"Cannot find agent column. Detected: {list(df.columns)}")
    if not disp_col:
        raise ValueError(f"Cannot find disposition column. Detected: {list(df.columns)}")

    # Filter rows without agent (abandoned/IVR)
    df = df[df[agent_col].notna()].copy()
    df = df[df[agent_col].astype(str).str.strip() != ""]

    # Clean agent names
    df["Agent"] = df[agent_col].apply(lambda x: str(x).strip().split("_")[0].capitalize())
    df = df[~df["Agent"].str.lower().isin(TEST_AGENT_NAMES)]

    # Classify dispositions
    df["DispositionClean"] = df[disp_col].apply(classify_disposition)

    # Campaign from CSV column first, fallback to agent map
    if "campaign name" in col_lower:
        csv_camp_col = col_lower["campaign name"]
        df["Campaign"] = df[csv_camp_col].map(CSV_CAMPAIGN_MAP).fillna(
            df["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown")
        )
    else:
        df["Campaign"] = df["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown")

    # Parse call date
    if date_col:
        df["CallDate"] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True).dt.date
    else:
        df["CallDate"] = date.today()

    # Infer report date for banner
    if date_col:
        try:
            parsed = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True).dropna()
            csv_date = parsed.dt.date.max().strftime("%d %b %Y")
        except Exception:
            csv_date = datetime.today().strftime("%d %b %Y")
    else:
        csv_date = datetime.today().strftime("%d %b %Y")

    # Parse duration (only > 0 counts as talk time)
    if dur_col:
        df["DurationSecs"] = df[dur_col].apply(parse_duration_seconds)
    else:
        df["DurationSecs"] = 0.0

    # Warnings
    warnings = []
    if df.empty:
        warnings.append("CSV has no data rows after filtering.")
    else:
        unknown = df.loc[~df["Agent"].isin(AGENT_CAMPAIGN_MAP), "Agent"].unique()
        if len(unknown):
            warnings.append(f"{len(unknown)} agent(s) not in campaign config: {', '.join(sorted(unknown)[:10])}")

    # Raw per-call frame — includes Date and Duration for filtering
    raw_df = df[["Agent", "DispositionClean", "Campaign", "CallDate", "DurationSecs"]].copy()
    raw_df.columns = ["Agent", "Disposition", "Campaign", "Date", "DurationSecs"]
    raw_df["Date"] = raw_df["Date"].astype(str)   # JSON-serialisable

    # Summary (full dataset, no date filter — filtering happens at render time)
    df["_cont"]     = df["DispositionClean"].isin(CONTACTED_DISPOSITIONS).astype(int)
    df["_not_cont"] = df["DispositionClean"].isin(NOT_CONTACTED_DISPOSITIONS).astype(int)

    summary = (
        df.groupby("Agent", as_index=False)
          .agg(
              Attempts    =("Agent",        "count"),
              Contacted   =("_cont",        "sum"),
              NotContacted=("_not_cont",    "sum"),
              TalkTimeSecs=("DurationSecs", "sum"),
          )
    )
    summary["Contact %"] = (summary["Contacted"] / summary["Attempts"] * 100).round(1)
    summary["Campaign"]  = summary["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown")
    summary = (
        summary[["Agent","Campaign","Attempts","Contacted","NotContacted","Contact %","TalkTimeSecs"]]
        .sort_values(["Campaign","Agent"])
        .reset_index(drop=True)
    )

    return summary, raw_df, csv_date, warnings


# ── Persistence ───────────────────────────────────────────────────────────────

def save_cache(agent_df: pd.DataFrame, raw_df: pd.DataFrame, csv_date: str) -> None:
    # Save to session_state first (survives page reruns within same session)
    st.session_state["_cache_agent"] = agent_df.to_dict(orient="records")
    st.session_state["_cache_raw"]   = raw_df.to_dict(orient="records")
    st.session_state["_cache_date"]  = csv_date
    # Also persist to JSON (survives browser refresh, lost on redeploy)
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({"date": csv_date, "data": agent_df.to_dict(orient="records")}, f)
        with open(CACHE_RAW_FILE, "w") as f:
            json.dump({"date": csv_date, "data": raw_df.to_dict(orient="records")}, f)
    except OSError as exc:
        logger.warning("JSON cache write failed (non-fatal): %s", exc)


def load_cache():
    # Try session_state first (fastest, most up-to-date)
    if "_cache_agent" in st.session_state and "_cache_date" in st.session_state:
        try:
            return pd.DataFrame(st.session_state["_cache_agent"]), st.session_state["_cache_date"]
        except Exception:
            pass
    # Fall back to JSON file
    if not os.path.exists(CACHE_FILE):
        return None, None
    try:
        with open(CACHE_FILE) as f:
            p = json.load(f)
        # Restore into session_state for faster future access
        st.session_state["_cache_agent"] = p["data"]
        st.session_state["_cache_date"]  = p["date"]
        return pd.DataFrame(p["data"]), p["date"]
    except (json.JSONDecodeError, KeyError, OSError) as exc:
        logger.warning("Summary cache unreadable (%s)", exc)
        return None, None


def load_raw_cache():
    # Try session_state first
    if "_cache_raw" in st.session_state and "_cache_date" in st.session_state:
        try:
            df = pd.DataFrame(st.session_state["_cache_raw"])
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
            return df, st.session_state["_cache_date"]
        except Exception:
            pass
    # Fall back to JSON file
    if not os.path.exists(CACHE_RAW_FILE):
        return None, None
    try:
        with open(CACHE_RAW_FILE) as f:
            p = json.load(f)
        df = pd.DataFrame(p["data"])
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        # Restore into session_state
        st.session_state["_cache_raw"]  = p["data"]
        st.session_state["_cache_date"] = p["date"]
        return df, p["date"]
    except (json.JSONDecodeError, KeyError, OSError) as exc:
        logger.warning("Raw cache unreadable (%s)", exc)
        return None, None


# ── Date filtering helpers ────────────────────────────────────────────────────

def get_mtd_range():
    """Return (first_of_month, today) for MTD default."""
    today = date.today()
    if today.year < 2026: today = date(2026, 4, 9)
    return date(today.year, today.month, 1), today


def filter_raw_by_dates(raw_df: pd.DataFrame, from_date: date, to_date: date) -> pd.DataFrame:
    """Filter raw per-call frame to a date range (inclusive)."""
    if "Date" not in raw_df.columns:
        return raw_df
    mask = (raw_df["Date"] >= from_date) & (raw_df["Date"] <= to_date)
    return raw_df[mask].copy()


def summarise_raw(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the summary frame from a (possibly filtered) raw_df.
    Returns same shape as process_csv summary.
    """
    if raw_df.empty:
        return pd.DataFrame(columns=["Agent","Campaign","Attempts","Contacted",
                                     "NotContacted","Contact %","TalkTimeSecs"])

    raw_df = raw_df.copy()
    raw_df["_cont"]     = raw_df["Disposition"].isin(CONTACTED_DISPOSITIONS).astype(int)
    raw_df["_not_cont"] = raw_df["Disposition"].isin(NOT_CONTACTED_DISPOSITIONS).astype(int)
    dur_col = raw_df["DurationSecs"] if "DurationSecs" in raw_df.columns else 0

    summary = (
        raw_df.groupby("Agent", as_index=False)
              .agg(
                  Attempts    =("Agent",     "count"),
                  Contacted   =("_cont",     "sum"),
                  NotContacted=("_not_cont", "sum"),
                  TalkTimeSecs=("DurationSecs", "sum") if "DurationSecs" in raw_df.columns
                               else ("_cont", "count"),
              )
    )
    summary["Contact %"] = (summary["Contacted"] / summary["Attempts"] * 100).round(1)
    summary["Campaign"]  = summary["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown")
    return (
        summary[["Agent","Campaign","Attempts","Contacted","NotContacted","Contact %","TalkTimeSecs"]]
        .sort_values(["Campaign","Agent"])
        .reset_index(drop=True)
    )


# ── Aggregation ───────────────────────────────────────────────────────────────

def campaign_totals(df, campaign: str):
    """Return (attempts, contacted, not_contacted, contact_pct, talk_secs)."""
    sub = df[df["Campaign"] == campaign]
    if sub.empty:
        return 0, 0, 0, 0.0, 0.0
    att      = int(sub["Attempts"].sum())
    cont     = int(sub["Contacted"].sum())
    not_cont = int(sub["NotContacted"].sum())
    pct      = round(cont / att * 100, 1) if att else 0.0
    talk     = float(sub["TalkTimeSecs"].sum()) if "TalkTimeSecs" in sub.columns else 0.0
    return att, cont, not_cont, pct, talk

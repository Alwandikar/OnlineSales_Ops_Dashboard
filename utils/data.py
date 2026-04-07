# utils/data.py
# ── All CSV parsing, caching, and data-access helpers ─────────────────────────

import io
import json
import logging
import os
from datetime import datetime

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
    """
    Map raw InTalk disposition string to one of the canonical values.

    Real InTalk format examples:
      "Follow up ➔ Call Back 2026-04-07 14:30:00"   -> Followup
      "Information Required ➔ Shared More Info ..."  -> Information Shared
      "Quote Sent ➔ Pricing Shared ..."              -> Quote Sent
      "Junk ➔ Wrong number  "                        -> Junk
      "Lost ➔ Not Interested  "                      -> Lost
      "Non Contactable ➔ Busy_Ringing  "             -> Not Contactable
      "Number in DNC List  "                         -> Not Contactable
      "Redial Call By Agent  "                       -> Not Contactable
      "-NA-  "  /  "  "  /  NaN                     -> Not Contactable
      "DISPOSITION ADDED BY SYSTEM  "               -> Not Contactable
    """
    if pd.isna(raw):
        return "Not Contactable"

    d = str(raw).strip()

    # Blank / system placeholders
    if not d or d in {"-NA-", "DISPOSITION ADDED BY SYSTEM"}:
        return "Not Contactable"

    # Real InTalk verbose dispositions (arrow format or plain)
    if d.startswith("Follow up")         or d.startswith("Followup"):
        return "Followup"
    if d.startswith("Information"):
        return "Information Shared"
    if d.startswith("Quote"):
        return "Quote Sent"
    if d.startswith("Junk"):
        return "Junk"
    if d.startswith("Lost"):
        return "Lost"
    if d.startswith("Non Contactable")   \
    or d.startswith("Number in DNC")     \
    or d.startswith("Redial"):
        return "Not Contactable"

    # Already-clean legacy values
    if d in ALL_DISPOSITIONS:
        return d

    # Anything else we don't recognise = not reached
    return "Not Contactable"


# ── CSV processing ────────────────────────────────────────────────────────────

def _find_column(col_map: dict, candidates: list) -> str | None:
    return next((col_map[k] for k in candidates if k in col_map), None)


def _extract_date_from_df(df: pd.DataFrame) -> str:
    """Infer the report date from date-like columns; fall back to today."""
    for col in df.columns:
        if any(kw in col.lower() for kw in ["date", "time", "created"]):
            try:
                parsed = pd.to_datetime(df[col], dayfirst=True, errors="coerce").dropna()
                if len(parsed) > 0:
                    return parsed.dt.date.mode()[0].strftime("%d %b %Y")
            except Exception:
                continue
    return datetime.today().strftime("%d %b %Y")


def _validate_csv(df: pd.DataFrame) -> list:
    """Return non-fatal data-quality warnings."""
    warnings = []
    if df.empty:
        warnings.append("CSV has no data rows after filtering.")
        return warnings

    unknown = df.loc[~df["Agent"].isin(AGENT_CAMPAIGN_MAP), "Agent"].unique()
    if len(unknown):
        warnings.append(
            f"{len(unknown)} agent(s) not in campaign config "
            f"(mapped to 'Unknown'): {', '.join(sorted(unknown)[:10])}"
        )
    return warnings


@st.cache_data(show_spinner=False)
def process_csv(file_bytes: bytes, filename: str):
    """
    Parse an InTalk Call History CSV export.

    InTalk prepends 3 metadata rows + 1 blank line before the real header:
        Row 0: From, "2026-04-06 00:00:00"
        Row 1: To,   "2026-04-06 23:59:59"
        Row 2: Report Date, "..."
        Row 3: (blank)
        Row 4: <real column headers>

    Returns: (summary_df, raw_df, csv_date, warnings)
    """
    buf = io.BytesIO(file_bytes)

    # ── Try skiprows=4 first (standard InTalk export) ─────────────────────────
    df = None
    for skip in [4, 5, 3, 0]:
        try:
            buf.seek(0)
            trial = pd.read_csv(buf, skiprows=skip, encoding="utf-8-sig",
                                on_bad_lines="skip", low_memory=False)
            col_lower = {c.lower().strip(): c for c in trial.columns}
            # Must have at least one agent-like column and one disposition-like column
            has_agent = any(k in col_lower for k in ["agent username", "agent name", "agent"])
            has_disp  = any(k in col_lower for k in ["disposition", "call status", "status"])
            if has_agent and has_disp:
                df = trial
                break
        except Exception as exc:
            logger.debug("skiprows=%d failed: %s", skip, exc)
            continue

    if df is None:
        raise ValueError(
            "Could not detect column headers. "
            "Make sure you're uploading the InTalk Call History CSV export."
        )

    col_lower = {c.lower().strip(): c for c in df.columns}

    # ── Locate required columns ───────────────────────────────────────────────
    agent_col = _find_column(col_lower, ["agent username", "agent name", "agent"])
    disp_col  = _find_column(col_lower, ["disposition", "call status", "status"])

    if agent_col is None:
        raise ValueError(f"Cannot find agent column. Detected: {list(df.columns)}")
    if disp_col is None:
        raise ValueError(f"Cannot find disposition column. Detected: {list(df.columns)}")

    # ── Filter rows without an agent (abandoned/IVR rows have no agent) ───────
    df = df[df[agent_col].notna()].copy()
    df = df[df[agent_col].astype(str).str.strip() != ""]

    # ── Clean agent names  e.g. "Kishan_Alwandikar" -> "Kishan" ──────────────
    df["Agent"] = df[agent_col].apply(
        lambda x: str(x).strip().split("_")[0].capitalize()
    )
    df = df[~df["Agent"].str.lower().isin(TEST_AGENT_NAMES)]

    # ── Classify dispositions ─────────────────────────────────────────────────
    df["DispositionClean"] = df[disp_col].apply(classify_disposition)

    # ── Campaign: prefer CSV campaign column, fall back to agent name map ──────
    if "campaign name" in col_lower:
        csv_camp_col = col_lower["campaign name"]
        df["Campaign"] = df[csv_camp_col].map(CSV_CAMPAIGN_MAP).fillna(
            df["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown")
        )
    else:
        df["Campaign"] = df["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown")

    # ── Infer report date ─────────────────────────────────────────────────────
    csv_date = _extract_date_from_df(df)

    # ── Data quality warnings ─────────────────────────────────────────────────
    warnings = _validate_csv(df)

    # ── Raw per-call frame (disposition page) ─────────────────────────────────
    raw_df = df[["Agent", "DispositionClean", "Campaign"]].copy()
    raw_df.columns = ["Agent", "Disposition", "Campaign"]

    # ── Summary frame (overview / leaderboard) ────────────────────────────────
    df["_cont"]     = df["DispositionClean"].isin(CONTACTED_DISPOSITIONS).astype(int)
    df["_not_cont"] = df["DispositionClean"].isin(NOT_CONTACTED_DISPOSITIONS).astype(int)

    summary = (
        df.groupby("Agent", as_index=False)
          .agg(
              Attempts    =("Agent",     "count"),
              Contacted   =("_cont",     "sum"),
              NotContacted=("_not_cont", "sum"),
          )
    )
    summary["Contact %"] = (summary["Contacted"] / summary["Attempts"] * 100).round(1)
    summary["Campaign"]  = summary["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown")
    summary = (
        summary[["Agent", "Campaign", "Attempts", "Contacted", "NotContacted", "Contact %"]]
        .sort_values(["Campaign", "Agent"])
        .reset_index(drop=True)
    )

    return summary, raw_df, csv_date, warnings


# ── Persistence ───────────────────────────────────────────────────────────────

def save_cache(agent_df: pd.DataFrame, raw_df: pd.DataFrame, csv_date: str) -> None:
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({"date": csv_date, "data": agent_df.to_dict(orient="records")}, f)
        with open(CACHE_RAW_FILE, "w") as f:
            json.dump({"date": csv_date, "data": raw_df.to_dict(orient="records")}, f)
    except OSError as exc:
        logger.error("Failed to write cache: %s", exc)
        raise


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None, None
    try:
        with open(CACHE_FILE) as f:
            p = json.load(f)
        return pd.DataFrame(p["data"]), p["date"]
    except (json.JSONDecodeError, KeyError, OSError) as exc:
        logger.warning("Summary cache unreadable (%s)", exc)
        return None, None


def load_raw_cache():
    if not os.path.exists(CACHE_RAW_FILE):
        return None, None
    try:
        with open(CACHE_RAW_FILE) as f:
            p = json.load(f)
        return pd.DataFrame(p["data"]), p["date"]
    except (json.JSONDecodeError, KeyError, OSError) as exc:
        logger.warning("Raw cache unreadable (%s)", exc)
        return None, None


# ── Aggregation ───────────────────────────────────────────────────────────────

def campaign_totals(df, campaign: str):
    """Return (attempts, contacted, not_contacted, contact_pct) for one campaign."""
    sub = df[df["Campaign"] == campaign]
    if sub.empty:
        return 0, 0, 0, 0.0
    att      = int(sub["Attempts"].sum())
    cont     = int(sub["Contacted"].sum())
    not_cont = int(sub["NotContacted"].sum())
    pct      = round(cont / att * 100, 1) if att else 0.0
    return att, cont, not_cont, pct

# utils/data.py — CSV parsing, aggregation, helpers

import io
import logging
from datetime import date

import pandas as pd

from utils.constants import (
    AGENT_CAMPAIGN_MAP, ALL_DISPOSITIONS, CONTACTED_DISPOSITIONS,
    CSV_CAMPAIGN_MAP, NOT_CONTACTED_DISPOSITIONS, TEST_AGENT_NAMES,
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


# ── Duration helper ───────────────────────────────────────────────────────────

def parse_duration_secs(val) -> float:
    try:
        if pd.isna(val): return 0.0
        td = pd.to_timedelta(str(val).strip(), errors="coerce")
        if pd.isna(td): return 0.0
        s = td.total_seconds()
        return s if s > 0 else 0.0
    except Exception:
        return 0.0


def format_duration(secs: float) -> str:
    secs = int(secs)
    h, rem = divmod(secs, 3600)
    m, s   = divmod(rem, 60)
    if h > 0: return f"{h}h {m}m"
    if m > 0: return f"{m}m {s}s"
    return f"{s}s"


# ── CSV parsing ───────────────────────────────────────────────────────────────

def parse_intalk_csv(file_bytes: bytes) -> tuple[pd.DataFrame, date, list]:
    """
    Parse an InTalk Call History CSV.
    Returns (raw_df, report_date, warnings).
    raw_df columns: Date, Agent, Campaign, Disposition, DurationSecs
    """
    buf = io.BytesIO(file_bytes)
    df  = None
    warnings = []

    for skip in [4, 5, 3, 0]:
        try:
            buf.seek(0)
            trial = pd.read_csv(buf, skiprows=skip, encoding="utf-8-sig",
                                on_bad_lines="skip", low_memory=False)
            col_lower = {c.lower().strip(): c for c in trial.columns}
            if any(k in col_lower for k in ["agent username","agent name","agent"]) \
               and any(k in col_lower for k in ["disposition","call status","status"]):
                df = trial
                break
        except Exception:
            continue

    if df is None:
        raise ValueError("Cannot detect column headers. Upload the InTalk Call History CSV.")

    col_lower  = {c.lower().strip(): c for c in df.columns}
    agent_col  = next((col_lower[k] for k in ["agent username","agent name","agent"] if k in col_lower), None)
    disp_col   = next((col_lower[k] for k in ["disposition","call status","status"] if k in col_lower), None)
    date_col   = next((col_lower[k] for k in ["date time","datetime","date"] if k in col_lower), None)
    dur_col    = col_lower.get("duration")
    camp_col   = col_lower.get("campaign name")

    # Filter rows without agent
    df = df[df[agent_col].notna()].copy()
    df = df[df[agent_col].astype(str).str.strip() != ""]
    df["Agent"] = df[agent_col].apply(lambda x: str(x).strip().split("_")[0].capitalize())
    df = df[~df["Agent"].str.lower().isin(TEST_AGENT_NAMES)]

    df["Disposition"] = df[disp_col].apply(classify_disposition)

    if camp_col:
        df["Campaign"] = df[camp_col].map(CSV_CAMPAIGN_MAP).fillna(
            df["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown"))
    else:
        df["Campaign"] = df["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown")

    # Extract date from file header (most reliable)
    report_date = date.today()
    try:
        raw_text = file_bytes.decode("utf-8-sig", errors="replace")
        for line in raw_text.split("\n")[:5]:
            if line.strip().lower().startswith("to,") or '"to"' in line.lower():
                date_str = line.split(",", 1)[-1].strip().strip('"').strip()
                parsed = pd.to_datetime(date_str, errors="coerce")
                if not pd.isna(parsed):
                    report_date = parsed.date()
                    break
    except Exception:
        pass

    # Parse call-level date for storage
    if date_col:
        df["Date"] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True).dt.date
    else:
        df["Date"] = report_date

    df["DurationSecs"] = df[dur_col].apply(parse_duration_secs) if dur_col else 0.0

    # Warnings
    unknown = df.loc[~df["Agent"].isin(AGENT_CAMPAIGN_MAP), "Agent"].unique()
    if len(unknown):
        warnings.append(f"{len(unknown)} agent(s) not in config: {', '.join(sorted(unknown)[:5])}")

    result = df[["Date", "Agent", "Campaign", "Disposition", "DurationSecs"]].copy()
    result["Date"] = result["Date"].astype(str)
    return result, report_date, warnings


# ── Aggregation ───────────────────────────────────────────────────────────────

def filter_by_dates(df: pd.DataFrame, from_date: date, to_date: date) -> pd.DataFrame:
    if df.empty: return df
    if "Date" not in df.columns: return df
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    return df[(df["Date"] >= from_date) & (df["Date"] <= to_date)].copy()


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    """One row per agent with Attempts / Contacted / NotContacted / Contact% / TalkTimeSecs."""
    if df.empty:
        return pd.DataFrame(columns=["Agent","Campaign","Attempts","Contacted",
                                     "NotContacted","Contact %","TalkTimeSecs"])
    df = df.copy()
    df["_cont"]  = df["Disposition"].isin(CONTACTED_DISPOSITIONS).astype(int)
    df["_nc"]    = df["Disposition"].isin(NOT_CONTACTED_DISPOSITIONS).astype(int)

    s = df.groupby("Agent", as_index=False).agg(
        Attempts    =("Agent",        "count"),
        Contacted   =("_cont",        "sum"),
        NotContacted=("_nc",          "sum"),
        TalkTimeSecs=("DurationSecs", "sum"),
    )
    s["Contact %"] = (s["Contacted"] / s["Attempts"] * 100).round(1)
    s["Campaign"]  = s["Agent"].map(AGENT_CAMPAIGN_MAP).fillna("Unknown")
    return s[["Agent","Campaign","Attempts","Contacted","NotContacted","Contact %","TalkTimeSecs"]] \
             .sort_values(["Campaign","Agent"]).reset_index(drop=True)


def campaign_totals(df: pd.DataFrame, campaign: str) -> dict:
    sub = df[df["Campaign"] == campaign]
    if sub.empty:
        return {"att":0,"cont":0,"nc":0,"pct":0.0,"talk":0.0}
    att  = int(sub["Attempts"].sum())
    cont = int(sub["Contacted"].sum())
    nc   = int(sub["NotContacted"].sum())
    talk = float(sub["TalkTimeSecs"].sum())
    pct  = round(cont/att*100, 1) if att else 0.0
    return {"att":att,"cont":cont,"nc":nc,"pct":pct,"talk":talk}

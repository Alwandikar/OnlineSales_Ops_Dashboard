# utils/github_store.py
# Reads and writes sales_data.csv stored in the GitHub repo.
# Uses the GitHub REST API with a Personal Access Token stored in Streamlit secrets.

import base64
import io
import logging

import pandas as pd
import requests
import streamlit as st

from utils.constants import GITHUB_REPO, GITHUB_DATA_PATH

logger = logging.getLogger(__name__)

# Column schema for the persistent CSV
SCHEMA = ["Date", "Agent", "Campaign", "Disposition", "DurationSecs"]


def _headers():
    token = st.secrets.get("GITHUB_TOKEN", "")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in Streamlit secrets.")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def _api_url():
    return f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_DATA_PATH}"


@st.cache_data(ttl=60, show_spinner=False)
def load_data() -> pd.DataFrame:
    """
    Load the full sales_data.csv from GitHub.
    Returns empty DataFrame with correct schema if file doesn't exist yet.
    """
    try:
        r = requests.get(_api_url(), headers=_headers(), timeout=15)
        if r.status_code == 404:
            return pd.DataFrame(columns=SCHEMA)
        r.raise_for_status()
        content = base64.b64decode(r.json()["content"]).decode("utf-8")
        df = pd.read_csv(io.StringIO(content))
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df["DurationSecs"] = pd.to_numeric(df["DurationSecs"], errors="coerce").fillna(0)
        return df
    except Exception as exc:
        logger.error("Failed to load data from GitHub: %s", exc)
        return pd.DataFrame(columns=SCHEMA)


def save_data(df: pd.DataFrame) -> bool:
    """
    Save (overwrite) the full sales_data.csv to GitHub.
    Returns True on success.
    """
    try:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        content_b64 = base64.b64encode(csv_bytes).decode("utf-8")

        # Get current SHA (needed for update)
        r = requests.get(_api_url(), headers=_headers(), timeout=15)
        sha = r.json().get("sha") if r.status_code == 200 else None

        payload = {
            "message": f"Update sales data — {df['Date'].max() if not df.empty else 'empty'}",
            "content": content_b64,
        }
        if sha:
            payload["sha"] = sha

        r2 = requests.put(_api_url(), headers=_headers(), json=payload, timeout=30)
        r2.raise_for_status()
        load_data.clear()  # bust the cache
        return True
    except Exception as exc:
        logger.error("Failed to save data to GitHub: %s", exc)
        return False


def append_day(new_df: pd.DataFrame, day_date) -> tuple[bool, str]:
    """
    Append or overwrite one day's data in the persistent store.
    If the date already exists, those rows are replaced (idempotent).
    Returns (success, message).
    """
    existing = load_data()

    # Remove existing rows for this date
    if not existing.empty and "Date" in existing.columns:
        existing["Date"] = pd.to_datetime(existing["Date"], errors="coerce").dt.date
        existing = existing[existing["Date"] != day_date]

    # Combine and sort
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined = combined.sort_values(["Date", "Agent"]).reset_index(drop=True)

    ok = save_data(combined)
    if ok:
        return True, f"✅ Data saved for {day_date.strftime('%d %b %Y')} — {len(new_df):,} rows added."
    return False, "❌ Failed to save data to GitHub. Check your GITHUB_TOKEN in Streamlit secrets."

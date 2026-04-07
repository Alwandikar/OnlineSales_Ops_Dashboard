# utils/styles.py
# ── Spotify-inspired dark theme — injected once per page ──────────────────────

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ─────────────────────────────────────────────────────────────────── */
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    color: #FFFFFF !important;
}
.stApp { background: #121212 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2.5rem 3rem !important; max-width: 1400px !important; }

/* Sidebar dark */
section[data-testid="stSidebar"] {
    background: #000000 !important;
    border-right: 1px solid #282828;
}
section[data-testid="stSidebar"] * { color: #B3B3B3 !important; }

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #181818 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid #282828 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #B3B3B3 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    border-radius: 8px !important;
    padding: .5rem 1.6rem !important;
    border: none !important;
    transition: all .2s !important;
}
.stTabs [aria-selected="true"] {
    background: #1DB954 !important;
    color: #000000 !important;
}
.stTabs [data-baseweb="tab-border"]     { display: none !important; }
.stTabs [data-baseweb="tab-highlight"]  { display: none !important; }

/* ── Top nav ──────────────────────────────────────────────────────────────── */
.top-nav {
    background: #000000;
    border-bottom: 1px solid #282828;
    padding: 1rem 2.5rem;
    margin: 0 -2.5rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 2px 20px rgba(0,0,0,.6);
}
.nav-brand { display: flex; align-items: center; gap: .75rem; }
.nav-logo  {
    width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
}
.nav-logo-overview .nav-logo-disp .nav-logo-leaderboard { background: #1DB954; }
.nav-title { font-size: 1.05rem; font-weight: 700; color: #FFFFFF; letter-spacing: -.01em; }
.nav-sub   { font-size: .72rem; color: #535353; }
.nav-tag   {
    font-size: .68rem; font-weight: 700; letter-spacing: .09em;
    text-transform: uppercase; padding: .35rem 1rem; border-radius: 999px;
    background: #1DB954; color: #000000;
}

/* ── Date banner ──────────────────────────────────────────────────────────── */
.date-banner {
    background: #181818; border: 1px solid #282828; border-radius: 12px;
    padding: .75rem 1.2rem; margin-bottom: 1.5rem;
    font-size: .85rem; color: #B3B3B3; font-weight: 500;
}
.date-banner strong { color: #1DB954; }

/* ── Section label ────────────────────────────────────────────────────────── */
.section-label {
    font-size: .68rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #535353; margin: 2rem 0 .9rem;
}

/* ── KPI cards ────────────────────────────────────────────────────────────── */
.kpi-card {
    background: #181818; border-radius: 12px; padding: 1.4rem 1.6rem 1.2rem;
    border: 1px solid #282828; position: relative; overflow: hidden;
    transition: background .2s, transform .2s; height: 100%;
}
.kpi-card:hover { background: #282828; transform: translateY(-2px); }
.kpi-accent-bar { position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 12px 12px 0 0; }
.kpi-label      { font-size: .68rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: #535353; margin-bottom: .5rem; }
.kpi-value      { font-size: 2.4rem; font-weight: 800; color: #FFFFFF; letter-spacing: -.04em; line-height: 1.1; }
.kpi-value-green{ color: #1DB954; }
.kpi-value-red  { color: #e85454; }
.kpi-value-pct  { color: #1DB954; }
.kpi-sub        { font-size: .72rem; color: #535353; margin-top: .4rem; }
.kpi-icon       { position: absolute; top: 1.2rem; right: 1.4rem; font-size: 1.4rem; opacity: .2; }

/* ── Disposition cards ────────────────────────────────────────────────────── */
.disp-card {
    background: #181818; border-radius: 12px; padding: 1.1rem 1.3rem;
    border: 1px solid #282828; position: relative; overflow: hidden;
    height: 100%; transition: background .2s, transform .15s;
}
.disp-card:hover { background: #282828; transform: translateY(-2px); }
.disp-accent  { position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 12px 12px 0 0; }
.disp-label   { font-size: .65rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; color: #535353; }
.disp-count   { font-size: 1.9rem; font-weight: 800; color: #FFFFFF; letter-spacing: -.03em; line-height: 1.1; }
.disp-pct     { font-size: .8rem; font-weight: 600; color: #B3B3B3; margin-top: .2rem; font-family: 'JetBrains Mono', monospace; }

/* ── Campaign block ───────────────────────────────────────────────────────── */
.campaign-block {
    background: #181818; border-radius: 16px; border: 1px solid #282828;
    padding: 1.8rem 2rem; margin-bottom: 1.5rem;
}
.campaign-chip {
    display: inline-flex; align-items: center; gap: .4rem;
    font-size: .68rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; padding: .3rem .9rem; border-radius: 999px; margin-bottom: .8rem;
}
.chip-sports  { background: rgba(29,185,84,.15);  color: #1DB954; border: 1px solid rgba(29,185,84,.3); }
.chip-holiday { background: rgba(30,215,96,.10);  color: #1ed760; border: 1px solid rgba(30,215,96,.2); }
.campaign-name { font-size: 1.4rem; font-weight: 800; color: #FFFFFF; letter-spacing: -.02em; margin: 0 0 .2rem; }
.campaign-desc { font-size: .8rem; color: #535353; }

/* ── Agent section ────────────────────────────────────────────────────────── */
.agent-section {
    background: #181818; border-radius: 16px; border: 1px solid #282828;
    padding: 1.6rem 1.8rem; margin-bottom: 1.2rem; transition: background .2s;
}
.agent-section:hover { background: #1f1f1f; }
.agent-name-header { font-size: 1.1rem; font-weight: 800; color: #FFFFFF; letter-spacing: -.01em; margin-bottom: .2rem; }
.agent-camp-chip   {
    display: inline-flex; align-items: center; gap: .3rem;
    font-size: .65rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; padding: .2rem .7rem; border-radius: 999px; margin-bottom: .8rem;
}

/* ── Leaderboard ──────────────────────────────────────────────────────────── */
.leaderboard-row {
    background: #181818; border-radius: 12px; border: 1px solid #282828;
    padding: .9rem 1.4rem; margin-bottom: .5rem;
    display: flex; align-items: center; gap: 1rem;
    transition: background .2s, transform .15s;
}
.leaderboard-row:hover { background: #282828; transform: translateY(-1px); }
.rank-badge {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: .85rem; font-weight: 800; flex-shrink: 0;
}
.rank-1 { background: #1DB954; color: #000; }
.rank-2 { background: #535353; color: #fff; }
.rank-3 { background: #333333; color: #B3B3B3; }
.rank-n { background: #282828; color: #535353; }
.lb-agent    { font-size: .95rem; font-weight: 700; color: #FFFFFF; }
.lb-camp     { font-size: .65rem; font-weight: 600; text-transform: uppercase; letter-spacing: .07em; color: #535353; }
.lb-bar-bg   { background: #282828; border-radius: 999px; height: 6px; overflow: hidden; }
.lb-bar-fill { height: 6px; border-radius: 999px; }
.lb-pct      { font-size: .95rem; font-weight: 800; min-width: 48px; text-align: right; font-family: 'JetBrains Mono', monospace; }

/* ── Admin ────────────────────────────────────────────────────────────────── */
.admin-box       { background: #181818; border: 1px solid #282828; border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem; }
.admin-box-title { font-size: .75rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #1DB954; margin-bottom: .8rem; }

/* ── Misc ─────────────────────────────────────────────────────────────────── */
.dash-divider { border: none; border-top: 1px solid #282828; margin: 1.8rem 0; }
.empty-state  { text-align: center; padding: 5rem 2rem; }
.empty-icon   { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-title  { font-size: 1.1rem; font-weight: 700; color: #B3B3B3; margin-bottom: .4rem; }
.empty-sub    { font-size: .85rem; color: #535353; }

section[data-testid="stFileUploadDropzone"] {
    background: #181818 !important; border: 2px dashed #333 !important; border-radius: 12px !important;
}
.stTextInput input {
    background: #282828 !important; color: #FFFFFF !important;
    border-color: #535353 !important; border-radius: 8px !important;
}
.stButton button {
    background: #1DB954 !important; color: #000000 !important;
    font-weight: 700 !important; border: none !important;
    border-radius: 999px !important;
}
.stButton button:hover { background: #1ed760 !important; }
.streamlit-expanderHeader {
    background: #181818 !important; color: #B3B3B3 !important; border-radius: 8px !important;
}
div[data-testid="metric-container"] { display: none; }
</style>
"""


def inject_css():
    """Call once at the top of each page."""
    import streamlit as st
    st.markdown(SHARED_CSS, unsafe_allow_html=True)

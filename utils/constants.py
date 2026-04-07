# utils/constants.py
# ── Single source of truth for all shared config ──────────────────────────────

ADMIN_PASSWORD = "CSonline2026"

CACHE_FILE     = "last_data.json"
CACHE_RAW_FILE = "last_raw.json"

TEST_AGENT_NAMES = {"testagent", "test_agent", "test agent", "test"}

CAMPAIGNS = {
    # Agent first-names produced by split('_')[0].capitalize()
    "Sports":  ["Kishan", "Dilip", "Dilipsingh", "Melito", "Gibson", "Gideon"],
    "Holiday": ["Vinay", "Brendan", "Ajinkya", "Khushbu"],
}

AGENT_CAMPAIGN_MAP = {agent: camp for camp, agents in CAMPAIGNS.items() for agent in agents}

# Raw CSV "Campaign name" values -> dashboard campaign label
# InTalk uses these exact strings in the export
CSV_CAMPAIGN_MAP = {
    "Dsg_PreviewAuto":     "Sports",
    "Holiday_PreviewAuto": "Holiday",
    "Holiday_Churn":       "Holiday",
    # "Inbound" and anything else -> "Unknown"
}

# ── Disposition logic ─────────────────────────────────────────────────────────
# "Contacted"     = call was answered / agent spoke to someone
# "Not Contacted" = line never picked up (busy, DNC, abandoned, system rows)

ALL_DISPOSITIONS = [
    "Followup",
    "Information Shared",
    "Quote Sent",
    "Junk",
    "Lost",
    "Not Contactable",
]

# Everything here = call was answered (a human was reached)
CONTACTED_DISPOSITIONS = {"Followup", "Information Shared", "Quote Sent", "Junk", "Lost"}

# Everything else = not reached
NOT_CONTACTED_DISPOSITIONS = {"Not Contactable"}

DISP_COLORS = {
    "Followup":          "#1DB954",
    "Information Shared":"#1ed760",
    "Quote Sent":        "#17a2b8",
    "Junk":              "#f59e0b",
    "Lost":              "#e85454",
    "Not Contactable":   "#535353",
}

DISP_ICONS = {
    "Followup":          "🔄",
    "Information Shared":"ℹ️",
    "Quote Sent":        "💬",
    "Junk":              "🗑️",
    "Lost":              "❌",
    "Not Contactable":   "📵",
}

CAMPAIGN_CONFIG = {
    "Sports": {
        "accent":     "#1DB954",
        "chip_class": "chip-sports",
        "emoji":      "🏅",
    },
    "Holiday": {
        "accent":     "#1ed760",
        "chip_class": "chip-holiday",
        "emoji":      "🏖️",
    },
}

# ── Design tokens ─────────────────────────────────────────────────────────────
FONT         = "DM Sans, sans-serif"
BG_BASE      = "#121212"
BG_ELEVATED  = "#181818"
BG_RAISED    = "#282828"
ACCENT_GREEN = "#1DB954"
TXT_PRIMARY  = "#FFFFFF"
TXT_SECONDARY= "#B3B3B3"
TXT_MUTED    = "#535353"
GRID         = "#282828"
TXTC         = "#B3B3B3"

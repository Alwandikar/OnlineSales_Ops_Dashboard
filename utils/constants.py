# utils/constants.py

ADMIN_PASSWORD = "CSonline2026"

CACHE_FILE     = "last_data.json"
CACHE_RAW_FILE = "last_raw.json"

TEST_AGENT_NAMES = {"testagent", "test_agent", "test agent", "test"}

CAMPAIGNS = {
    "Sports":  ["Kishan", "Dilip", "Dilipsingh", "Melito", "Gibson", "Gideon"],
    "Holiday": ["Vinay", "Brendan", "Ajinkya", "Khushbu"],
}

AGENT_CAMPAIGN_MAP = {agent: camp for camp, agents in CAMPAIGNS.items() for agent in agents}

CSV_CAMPAIGN_MAP = {
    "Dsg_PreviewAuto":     "Sports",
    "Holiday_PreviewAuto": "Holiday",
    "Holiday_Churn":       "Holiday",
}

ALL_DISPOSITIONS = [
    "Followup",
    "Information Shared",
    "Quote Sent",
    "Junk",
    "Lost",
    "Not Contactable",
]

CONTACTED_DISPOSITIONS     = {"Followup", "Information Shared", "Quote Sent", "Junk", "Lost"}
NOT_CONTACTED_DISPOSITIONS = {"Not Contactable"}

DISP_COLORS = {
    "Followup":          "#0047CC",
    "Information Shared":"#047857",
    "Quote Sent":        "#6D28D9",
    "Junk":              "#B45309",
    "Lost":              "#B91C1C",
    "Not Contactable":   "#6B7280",
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
        "accent":     "#0047CC",
        "chip_class": "chip-sports",
        "emoji":      "🏅",
    },
    "Holiday": {
        "accent":     "#047857",
        "chip_class": "chip-holiday",
        "emoji":      "🏖️",
    },
}

# ── DSG Brand tokens ──────────────────────────────────────────────────────────
# Extracted from dreamsetgo.com: dark navy nav, white surface, gold accent
DSG_NAVY   = "#0A0E1A"   # top nav / sidebar
DSG_GOLD   = "#C9A035"   # primary accent (buttons, active tabs, highlights)
DSG_GOLD_L = "#E8BE52"   # hover gold
DSG_WHITE  = "#FFFFFF"
DSG_BG     = "#F5F6F8"   # page background
DSG_CARD   = "#FFFFFF"   # card background
DSG_BORDER = "#E2E5EC"
DSG_TEXT   = "#0A0E1A"   # primary text
DSG_MUTED  = "#6B7280"   # secondary text
DSG_SUBTLE = "#9CA3AF"   # labels

FONT  = "DM Sans, sans-serif"
GRID  = "#F0F2F5"
TXTC  = "#6B7280"

# utils/constants.py — Single source of truth

ADMIN_PASSWORD = "CSonline2026"

# GitHub storage
GITHUB_REPO     = "Alwandikar/OnlineSales_Ops_Dashboard"
GITHUB_DATA_PATH = "data/sales_data.csv"

# Agents & campaigns
CAMPAIGNS = {
    "Sports":  ["Kishan", "Dilip", "Dilipsingh", "Melito", "Gibson", "Gideon"],
    "Holiday": ["Vinay", "Brendan", "Ajinkya", "Khushbu"],
}
AGENT_CAMPAIGN_MAP = {a: c for c, agents in CAMPAIGNS.items() for a in agents}

CSV_CAMPAIGN_MAP = {
    "Dsg_PreviewAuto":     "Sports",
    "Holiday_PreviewAuto": "Holiday",
    "Holiday_Churn":       "Holiday",
}

TEST_AGENT_NAMES = {"testagent", "test_agent", "test agent", "test"}

# Dispositions
ALL_DISPOSITIONS = ["Followup", "Information Shared", "Quote Sent", "Junk", "Lost", "Not Contactable"]
CONTACTED_DISPOSITIONS     = {"Followup", "Information Shared", "Quote Sent", "Junk", "Lost"}
NOT_CONTACTED_DISPOSITIONS = {"Not Contactable"}

DISP_COLORS = {
    "Followup":          "#0A84FF",
    "Information Shared":"#30D158",
    "Quote Sent":        "#BF5AF2",
    "Junk":              "#FF9F0A",
    "Lost":              "#FF453A",
    "Not Contactable":   "#636366",
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
    "Sports":  {"accent": "#0A84FF", "chip": "chip-sports",  "emoji": "🏅"},
    "Holiday": {"accent": "#30D158", "chip": "chip-holiday", "emoji": "🏖️"},
}

# iOS dark theme tokens
BG_BASE      = "#000000"
BG_CARD      = "#1C1C1E"
BG_ELEVATED  = "#2C2C2E"
BG_SEPARATOR = "#38383A"
TXT_PRIMARY  = "#FFFFFF"
TXT_SECONDARY= "#EBEBF5"
TXT_MUTED    = "#8E8E93"
ACCENT_BLUE  = "#0A84FF"
ACCENT_GREEN = "#30D158"
ACCENT_RED   = "#FF453A"
ACCENT_GOLD  = "#FFD60A"
FONT         = "SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif"
GRID         = "#2C2C2E"
TXTC         = "#8E8E93"

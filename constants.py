from typing import Any, Dict

# Custom Types
StravaActivity = Dict[str, Any]
StravaAthlete = Dict[str, Any]

# Colors
BG_TOP = (18, 18, 20)
BG_BOTTOM = (30, 30, 35)
MAP_BG = (15, 15, 18)
STRAVA_ORANGE = (252, 76, 2)
TEXT_PRIMARY = (255, 255, 255)
TEXT_MUTED = (180, 180, 185)

# Canvas
W, H = 1080, 1920

# Fonts (macOS paths shown — adjust if needed)
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"


# Activity type to Instagram title names
ACTIVITY_TO_TITLE_NAMES = {
    "Run": "Running",
    "Ride": "Cycling",
    "AlpineSki": "Skiing",
    "Hike": "Hiking",
    "Walk": "Walking",
}

ACTIVITY_TO_BADGE_ICON = {
    "Run": "🏃🏻‍♀️",
    "Ride": "🚴🏻‍♀️",
    "AlpineSki": "⛷️",
    "Hike": "🥾",
    "Walk": "🚶🏻‍♀️",
}

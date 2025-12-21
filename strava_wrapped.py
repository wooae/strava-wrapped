import os
from datetime import datetime
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
from strava_client import StravaAthlete, StravaClient

from constants import *
from image_helpers import *


CLIENT_ID = "191048"
CLIENT_SECRET = "144564ca8c0f53538149ad27c8ea46a963b3f0c5"
YEAR = 2025


def top_k_sports_summary(summary_df: pd.DataFrame, athlete: StravaAthlete, k: int = 5) -> None:
    """Creates a Instagram story summarizing the athlete's top K sports activity types based on count

    Args:
        summary_df (pd.DataFrame): DataFrame containing activities summary by sport
        athlete (StravaAthlete): athlete data
        k (int, optional): top K activities to include in summary. Defaults to 5. Must be less than or equal to 5.
    """
    first_name = athlete["firstname"]

    if k > 5:
        raise ValueError("Error: please enter a k value less than or equal to 5 (it will look better for the gram).")

    # generate Instagram story graphic
    fig, ax = plt.subplots(figsize=(6, 10), facecolor="#f0f0f0")
    top_k = summary_df.head(k)
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
    bars = ax.barh(top_k.index, top_k["count"], color=colors[: len(top_k)], edgecolor="black", linewidth=0.5)
    ax.set_title(f"{first_name}'s {YEAR} Strava WRAPPED", fontsize=24, fontweight="bold", color="#2C3E50", pad=20)
    ax.set_xlabel("Number of Activities", fontsize=16, labelpad=10)
    ax.invert_yaxis()  # Highest count at top
    # Add value labels and details
    for i, (idx, row) in enumerate(top_k.iterrows()):
        ax.text(
            row["count"] + 0.5,
            i,
            f"{int(row['count'])} activities\n{row['total_distance_miles']:.1f} mi\n{row['total_elevation_gain_ft']:.0f} ft",
            ha="left",
            va="center",
            fontsize=14,
            fontweight="bold",
            color="#2C3E50",
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.5)
    ax.spines["bottom"].set_linewidth(0.5)
    plt.tight_layout()
    plt.savefig(f"strava_summary_{YEAR}.png", dpi=300, bbox_inches="tight", facecolor="#f0f0f0")
    print(f"\nSaved graphic to strava_summary_{YEAR}.png")


def sport_summary(stats: Dict[str, float], athlete: StravaAthlete) -> None:
    """Creates an Instagram story for the specified activity in stats

    Args:
        stats (Dict[str, Float]): dictionary containing activity stats for a particular type of activity
        athlete (StravaAthlete): athlete data
    """
    # create canvas and background
    img = Image.new("RGB", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)

    for y in range(H):
        ratio = y / H
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # profile photo
    avatar = load_image_from_url(athlete["profile_medium"], (220, 220))
    avatar = circular_crop(avatar)
    img.paste(avatar, (80, 100), avatar)

    # title
    title_font = ImageFont.truetype(FONT_BOLD, 90)
    subtitle_font = ImageFont.truetype(FONT_REG, 46)

    activity_type = stats["type"]
    first_name = athlete["firstname"]
    draw.text((340, 120), ACTIVITY_TO_TITLE_NAMES.get(activity_type, activity_type), font=title_font, fill=TEXT_PRIMARY)
    draw.text((340, 240), f"{first_name}'s {YEAR} WRAPPED", font=subtitle_font, fill=TEXT_MUTED)

    # activity badge
    badge_center = (W - 250, 1600)
    badge_radius = 180

    draw.ellipse(
        [
            badge_center[0] - badge_radius,
            badge_center[1] - badge_radius,
            badge_center[0] + badge_radius,
            badge_center[1] + badge_radius,
        ],
        fill=STRAVA_ORANGE,
    )
    badge_icon_path = os.path.join("assets", f"{stats['type']}.png")
    icon = Image.open(badge_icon_path).convert("RGBA").resize((360, 360))
    img.paste(
        icon,
        (badge_center[0] - 180, badge_center[1] - 180),
        icon,
    )

    # stats section
    stat_title_font = ImageFont.truetype(FONT_REG, 44)
    stat_value_font = ImageFont.truetype(FONT_BOLD, 64)

    stats_y = 520
    row_gap = 140

    display_stats = [
        (f"{activity_type.upper()}S", f"{stats['count']}"),
        ("DISTANCE", f"{int(stats['total_distance_miles'])} miles"),
        ("ELEVATION", f"{int(stats['total_elevation_gain_ft'])} ft"),
        ("TIME", format_time(stats["moving_time_s"])),
    ]

    for i, (label, value) in enumerate(display_stats):
        y = stats_y + i * row_gap

        draw.text((120, y), label, font=stat_title_font, fill=TEXT_MUTED)
        draw.text((120, y + 50), value, font=stat_value_font, fill=TEXT_PRIMARY)

    # save
    OUTPUT_FILE = f"{stats['type']}_wrapped.png"
    img.save(OUTPUT_FILE)
    print(f"Saved Instagram story to {OUTPUT_FILE}")


def main():
    client = StravaClient(CLIENT_ID, CLIENT_SECRET)

    # Run OAuth once
    if not client.tokens:
        client.authenticate()

    print(f"Fetching athlete profile...")
    athlete = client.get_athlete_profile()
    first_name = athlete["firstname"]
    profile_pic_small = athlete["profile_medium"]

    start_of_year = datetime(YEAR, 1, 1)

    print(f"Fetching activities since {start_of_year.date()}...")
    activities = client.get_activities(start_of_year)

    print(f"Fetched {len(activities)} activities")

    df = pd.DataFrame(activities)

    # Convert useful fields
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["distance_km"] = df["distance"] / 1000
    df["distance_miles"] = df["distance_km"] * 0.621371
    df["total_elevation_gain_ft"] = df["total_elevation_gain"] * 3.28084
    df["moving_time_hr"] = df["moving_time"] / 3600

    print("\nSummary by sport:")
    summary_df = (
        df.groupby("type")
        .agg(
            count=("type", "size"),
            total_distance_miles=("distance_miles", "sum"),
            total_elevation_gain_ft=("total_elevation_gain_ft", "sum"),
            moving_time_s=("moving_time", "sum"),
        )
        .sort_values("count", ascending=False)
    )
    print(summary_df.head(5))
    summary_df = summary_df.reset_index()

    # Save raw data
    df.to_csv(f"strava_activities_{YEAR}.csv", index=False)
    print(f"\nSaved to strava_activities_{YEAR}.csv")

    run_stats = summary_df[summary_df["type"] == "Run"].to_dict(orient="records")[0]
    ride_stats = summary_df[summary_df["type"] == "Ride"].to_dict(orient="records")[0]
    sport_summary(stats=run_stats, athlete=athlete)
    sport_summary(stats=ride_stats, athlete=athlete)

    # top_k_sports_summary(summary_df=summary_df, athlete=athlete, k=5)


if __name__ == "__main__":
    main()

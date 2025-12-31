import polyline
import requests
from datetime import timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from constants import *


def format_time(seconds):
    td = timedelta(seconds=int(seconds))
    hours = td.seconds // 3600 + td.days * 24
    minutes = (td.seconds % 3600) // 60
    return f"{hours}h {minutes}m"


def format_number_with_commas(n):
    s = str(n)
    if "." in s:
        integer, decimal = s.split(".")
        decimal = "." + decimal
    else:
        integer, decimal = s, ""

    sign = ""
    if integer.startswith("-"):
        sign = "-"
        integer = integer[1:]

    parts = []
    while integer:
        parts.append(integer[-3:])
        integer = integer[:-3]

    return sign + ",".join(reversed(parts)) + decimal


def load_image_from_url(url, size):
    r = requests.get(url)
    r.raise_for_status()
    img = Image.open(BytesIO(r.content)).convert("RGBA")
    return img.resize(size)


def circular_crop(img):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
    img.putalpha(mask)
    return img


def render_route_map(
    encoded_polyline,
    size=(900, 900),
    line_width=6,
    line_color=(252, 76, 2),
    bg_color=(20, 20, 24),
):
    coords = polyline.decode(encoded_polyline)

    lats = [lat for lat, lon in coords]
    lons = [lon for lat, lon in coords]

    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    def project(lat, lon):
        x = (lon - min_lon) / (max_lon - min_lon + 1e-9)
        y = (lat - min_lat) / (max_lat - min_lat + 1e-9)
        return (
            int(x * (size[0] - 40) + 20),
            int((1 - y) * (size[1] - 40) + 20),
        )

    points = [project(lat, lon) for lat, lon in coords]

    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)

    draw.line(points, fill=line_color, width=line_width, joint="curve")

    return img


def generate_activity_story(activity: StravaActivity, width: int, height: int, title: str = "LONGEST ACTIVITY"):
    img = Image.new("RGB", (width, height), MAP_BG)
    draw = ImageDraw.Draw(img)

    # Scale factors based on default W=1080, H=1920
    scale_x = width / 1080
    scale_y = height / 1920

    # Font sizes scaled
    header_font_size = int(128 * scale_y)
    activity_name_font_size = int(128 * scale_y)
    stat_label_font_size = int(86 * scale_y)
    stat_value_font_size = int(112 * scale_y)

    header_font = ImageFont.truetype(FONT_BOLD, header_font_size)
    activity_name_font = ImageFont.truetype(FONT_BOLD, activity_name_font_size)
    stat_label_font = ImageFont.truetype(FONT_REG, stat_label_font_size)
    stat_value_font = ImageFont.truetype(FONT_BOLD, stat_value_font_size)

    # Title above map
    title_x = int(90 * scale_y)
    title_y = int(40 * scale_y)
    draw.text(
        (title_x, title_y),
        title,
        font=header_font,
        fill=TEXT_PRIMARY,
    )

    # Map size proportional
    map_size = (int(900 * scale_x), int(900 * scale_y))
    map_img = render_route_map(
        activity["map"]["summary_polyline"],
        size=map_size,
    )

    map_x = int(90 * scale_x)
    map_y = int(180 * scale_y)
    img.paste(map_img, (map_x, map_y))

    activity_name_x = int(90 * scale_y)
    activity_name_y = int(1100 * scale_y)
    draw.text(
        (activity_name_x, activity_name_y),
        activity["name"],
        font=activity_name_font,
        fill=TEXT_PRIMARY,
    )

    stats = [
        ("KUDOS", str(activity["kudos_count"])),
        ("DISTANCE", f"{activity['distance'] / 1000 * 0.621371:.2f} miles"),
        ("TIME", format_time(activity["moving_time"])),
    ]

    stats_y = int(1300 * scale_y)
    gap = int(200 * scale_y)

    for label, value in stats:
        draw.text((title_x, stats_y), label, font=stat_label_font, fill=TEXT_MUTED)
        draw.text((title_x, stats_y + int(100 * scale_y)), value, font=stat_value_font, fill=TEXT_PRIMARY)
        stats_y += gap

    # accent bar
    bar_x1 = int(90 * scale_x)
    bar_y1 = int(1040 * scale_y)
    bar_x2 = int(240 * scale_x)
    bar_y2 = int(1052 * scale_y)
    draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill=STRAVA_ORANGE)

    return img

import requests
from datetime import timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def format_time(seconds):
    td = timedelta(seconds=int(seconds))
    hours = td.seconds // 3600 + td.days * 24
    minutes = (td.seconds % 3600) // 60
    return f"{hours}h {minutes}m"


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

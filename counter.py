from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip
from pathlib import Path
import json
import random

TOKEN_FILE = "token.json"
HISTORY_FILE = "history.json"
IMAGE_FILE = "frame.png"
VIDEO_FILE = "subscriber_video.mp4"

WIDTH = 1920
HEIGHT = 1080


def get_font(size, bold=False):
    paths = []

    if bold:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
    else:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]

    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


# =========================
# YOUTUBE
# =========================

credentials = Credentials.from_authorized_user_file(TOKEN_FILE)

youtube = build(
    "youtube",
    "v3",
    credentials=credentials
)

data = youtube.channels().list(
    part="snippet,statistics",
    mine=True
).execute()["items"][0]

channel_name = data["snippet"]["title"]

subscribers = int(
    data["statistics"].get("subscriberCount", 0)
)

print("Chaîne :", channel_name)
print("Abonnés :", subscribers)


# =========================
# HISTORIQUE
# =========================

history_path = Path(HISTORY_FILE)

if history_path.exists():
    try:
        history = json.loads(
            history_path.read_text(encoding="utf-8")
        )
    except Exception:
        history = {}
else:
    history = {}

previous = history.get("last_subscribers")

if previous is None:
    gained = 0
    lost = 0
else:
    difference = subscribers - int(previous)

    gained = max(difference, 0)
    lost = max(-difference, 0)


# Objectif
goal = subscribers + max(gained, 1)


# =========================
# IMAGE
# =========================

image = Image.new(
    "RGB",
    (WIDTH, HEIGHT),
    (10, 12, 20)
)

draw = ImageDraw.Draw(image)


# =========================
# DÉCOR ALÉATOIRE
# =========================

event = random.choice([
    "stars",
    "circles",
    "dots",
    "lines"
])

if event == "stars":

    for _ in range(100):

        x = random.randint(20, WIDTH - 20)
        y = random.randint(20, HEIGHT - 20)
        r = random.randint(1, 4)

        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=(70, 75, 100)
        )

elif event == "circles":

    for _ in range(15):

        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        r = random.randint(30, 120)

        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            outline=(30, 35, 55),
            width=3
        )

elif event == "dots":

    for _ in range(150):

        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)

        draw.ellipse(
            (x, y, x+4, y+4),
            fill=(45, 50, 70)
        )

elif event == "lines":

    for _ in range(15):

        x = random.randint(0, WIDTH)

        draw.line(
            (x, 0, WIDTH-x, HEIGHT),
            fill=(25, 30, 50),
            width=3
        )


# =========================
# POLICES
# =========================

font_title = get_font(48, True)
font_counter = get_font(125, True)
font_info = get_font(43, True)
font_small = get_font(32, False)


# =========================
# TITRE
# =========================

draw.text(
    (WIDTH // 2, 95),
    channel_name,
    font=font_title,
    fill=(245, 245, 250),
    anchor="mm"
)

draw.text(
    (WIDTH // 2, 175),
    "SUBSCRIBER COUNTER",
    font=font_small,
    fill=(145, 150, 165),
    anchor="mm"
)


# =========================
# COMPTEUR
# =========================

draw.text(
    (WIDTH // 2, 385),
    f"{subscribers:,}",
    font=font_counter,
    fill=(245, 245, 250),
    anchor="mm"
)

draw.text(
    (WIDTH // 2, 485),
    "SUBSCRIBERS",
    font=font_small,
    fill=(145, 150, 165),
    anchor="mm"
)


# =========================
# GAGNÉS / PERDUS
# =========================

draw.rounded_rectangle(
    (300, 570, 850, 700),
    radius=25,
    fill=(20, 45, 30)
)

draw.rounded_rectangle(
    (1070, 570, 1620, 700),
    radius=25,
    fill=(55, 25, 30)
)

draw.text(
    (575, 635),
    f"+{gained:,} THIS HOUR",
    font=font_info,
    fill=(90, 230, 130),
    anchor="mm"
)

draw.text(
    (1345, 635),
    f"-{lost:,} LOST",
    font=font_info,
    fill=(255, 100, 100),
    anchor="mm"
)


# =========================
# OBJECTIF
# =========================

draw.text(
    (WIDTH // 2, 780),
    "NEXT HOUR GOAL",
    font=font_small,
    fill=(145, 150, 165),
    anchor="mm"
)

draw.text(
    (WIDTH // 2, 845),
    f"{goal:,}",
    font=font_info,
    fill=(245, 245, 250),
    anchor="mm"
)


# =========================
# PROGRESSION 100K
# =========================

draw.text(
    (WIDTH // 2, 920),
    "ROAD TO 100,000",
    font=font_small,
    fill=(145, 150, 165),
    anchor="mm"
)

bar_left = 500
bar_right = 1420
bar_top = 960
bar_bottom = 985

draw.rounded_rectangle(
    (bar_left, bar_top, bar_right, bar_bottom),
    radius=12,
    fill=(35, 40, 55)
)

progress = min(
    subscribers / 100000,
    1
)

progress_width = int(
    (bar_right - bar_left) * progress
)

if progress_width > 0:

    draw.rounded_rectangle(
        (
            bar_left,
            bar_top,
            bar_left + progress_width,
            bar_bottom
        ),
        radius=12,
        fill=(255, 70, 70)
    )


# =========================
# SAUVEGARDE
# =========================

image.save(IMAGE_FILE)

print("Image créée.")


# =========================
# VIDÉO
# =========================

print("Création de la vidéo...")

clip = ImageClip(IMAGE_FILE).with_duration(30)

clip.write_videofile(
    VIDEO_FILE,
    fps=30,
    codec="libx264",
    audio=False,
    logger=None
)

clip.close()

print("Vidéo créée.")


# =========================
# UPLOAD
# =========================

print("Upload sur YouTube...")

title = f"{subscribers:,} Subscribers - Hourly Update"

description = f"""Current subscribers: {subscribers:,}

Subscribers gained since last update: +{gained:,}
Subscribers lost since last update: -{lost:,}

Next hour goal: {goal:,}

Road to 100,000 subscribers.

Automatically updated every hour.
"""

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": title[:100],
            "description": description,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    },
    media_body=MediaFileUpload(
        VIDEO_FILE,
        mimetype="video/mp4",
        resumable=True
    )
)

response = request.execute()

print("==============================")
print("       VIDÉO PUBLIÉE !")
print("==============================")
print(
    "https://youtube.com/watch?v="
    + response["id"]
)
print("==============================")


# =========================
# HISTORIQUE
# =========================

history["last_subscribers"] = subscribers

history_path.write_text(
    json.dumps(
        history,
        indent=2
    ),
    encoding="utf-8"
)

print("Terminé !")

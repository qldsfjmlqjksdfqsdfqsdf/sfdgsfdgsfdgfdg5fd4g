from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip
from pathlib import Path
import json
import random


# ==========================================
# CONFIGURATION
# ==========================================

TOKEN_FILE = "token.json"
HISTORY_FILE = "history.json"
IMAGE_FILE = "frame.png"
VIDEO_FILE = "subscriber_video.mp4"


# ==========================================
# POLICES COMPATIBLES WINDOWS + GITHUB
# ==========================================

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


# ==========================================
# CONNEXION YOUTUBE
# ==========================================

print("Connexion à YouTube...")

credentials = Credentials.from_authorized_user_file(
    TOKEN_FILE
)

youtube = build(
    "youtube",
    "v3",
    credentials=credentials
)


# ==========================================
# RÉCUPÉRATION DE LA CHAÎNE
# ==========================================

data = youtube.channels().list(
    part="snippet,statistics",
    mine=True
).execute()["items"][0]

name = data["snippet"]["title"]

subscribers = int(
    data["statistics"].get(
        "subscriberCount",
        0
    )
)

print()
print("Chaîne :", name)
print("Abonnés :", subscribers)


# ==========================================
# HISTORIQUE
# ==========================================

history_file = Path(HISTORY_FILE)

if history_file.exists():

    try:
        history = json.loads(
            history_file.read_text(
                encoding="utf-8"
            )
        )

    except Exception:
        history = {"last": None}

else:

    history = {"last": None}


last = history.get("last")


if last is None:

    gained = 0
    lost = 0

else:

    difference = subscribers - int(last)

    gained = max(
        difference,
        0
    )

    lost = max(
        -difference,
        0
    )


# ==========================================
# OBJECTIF
# ==========================================

goal = subscribers + max(
    gained,
    1
)


# ==========================================
# ÉVÉNEMENT ALÉATOIRE
# ==========================================

event = random.choice([
    "normal",
    "stars",
    "lines",
    "circles",
    "dots"
])


# ==========================================
# CRÉATION DE L'IMAGE
# ==========================================

print("Création de l'image...")


WIDTH = 1920
HEIGHT = 1080


image = Image.new(
    "RGB",
    (WIDTH, HEIGHT),
    (10, 12, 20)
)

draw = ImageDraw.Draw(image)


# Polices

font_title = get_font(
    55,
    True
)

font_big = get_font(
    150,
    True
)

font_medium = get_font(
    55,
    True
)

font_small = get_font(
    42,
    False
)


# ==========================================
# DÉCOR ALÉATOIRE
# ==========================================

if event == "stars":

    for i in range(80):

        x = random.randint(
            30,
            WIDTH - 30
        )

        y = random.randint(
            30,
            HEIGHT - 30
        )

        r = random.randint(
            2,
            6
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r
            ),
            fill=(80, 90, 130)
        )


elif event == "lines":

    for i in range(12):

        x = random.randint(
            0,
            WIDTH
        )

        draw.line(
            (
                x,
                0,
                WIDTH - x,
                HEIGHT
            ),
            fill=(25, 30, 50),
            width=4
        )


elif event == "circles":

    for i in range(12):

        x = random.randint(
            0,
            WIDTH
        )

        y = random.randint(
            0,
            HEIGHT
        )

        r = random.randint(
            20,
            100
        )

        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r
            ),
            outline=(30, 35, 60),
            width=4
        )


elif event == "dots":

    for i in range(100):

        x = random.randint(
            0,
            WIDTH
        )

        y = random.randint(
            0,
            HEIGHT
        )

        draw.ellipse(
            (
                x,
                y,
                x + 5,
                y + 5
            ),
            fill=(40, 45, 70)
        )


# ==========================================
# TITRE
# ==========================================

draw.text(
    (
        WIDTH // 2,
        250
    ),
    name,
    font=font_title,
    fill=(245, 245, 250),
    anchor="mm"
)


# ==========================================
# SUBSCRIBERS
# ==========================================

draw.text(
    (
        WIDTH // 2,
        480
    ),
    "SUBSCRIBERS",
    font=font_medium,
    fill=(160, 165, 180),
    anchor="mm"
)


draw.text(
    (
        WIDTH // 2,
        720
    ),
    f"{subscribers:,}",
    font=font_big,
    fill=(245, 245, 250),
    anchor="mm"
)


# ==========================================
# GAGNÉS
# ==========================================

draw.text(
    (
        WIDTH // 2,
        980
    ),
    f"+{gained:,} THIS HOUR",
    font=font_medium,
    fill=(80, 220, 120),
    anchor="mm"
)


# ==========================================
# PERDUS
# ==========================================

draw.text(
    (
        WIDTH // 2,
        1080
    ),
    f"-{lost:,} LOST",
    font=font_medium,
    fill=(255, 80, 80),
    anchor="mm"
)


# ==========================================
# OBJECTIF
# ==========================================

draw.text(
    (
        WIDTH // 2,
        1280
    ),
    "NEXT HOUR GOAL",
    font=font_small,
    fill=(160, 165, 180),
    anchor="mm"
)


draw.text(
    (
        WIDTH // 2,
        1370
    ),
    f"{goal:,}",
    font=font_medium,
    fill=(245, 245, 250),
    anchor="mm"
)


# ==========================================
# OBJECTIF 100K
# ==========================================

draw.text(
    (
        WIDTH // 2,
        1650
    ),
    "ROAD TO 100,000",
    font=font_small,
    fill=(160, 165, 180),
    anchor="mm"
)


# Barre de progression

bar_x1 = 150
bar_x2 = WIDTH - 150
bar_y = 1720

draw.rounded_rectangle(
    (
        bar_x1,
        bar_y,
        bar_x2,
        bar_y + 25
    ),
    radius=12,
    fill=(35, 40, 55)
)


progress = min(
    subscribers / 100000,
    1
)


progress_width = int(
    (bar_x2 - bar_x1) * progress
)


if progress_width > 0:

    draw.rounded_rectangle(
        (
            bar_x1,
            bar_y,
            bar_x1 + progress_width,
            bar_y + 25
        ),
        radius=12,
        fill=(255, 70, 70)
    )


# ==========================================
# SAUVEGARDE IMAGE
# ==========================================

image.save(
    IMAGE_FILE
)

print("Image créée.")


# ==========================================
# CRÉATION VIDÉO
# ==========================================

print("Création de la vidéo...")


clip = ImageClip(
    IMAGE_FILE
).with_duration(
    30
)


clip.write_videofile(
    VIDEO_FILE,
    fps=30,
    codec="libx264",
    audio=False,
    logger=None
)


clip.close()


print("Vidéo créée.")


# ==========================================
# UPLOAD YOUTUBE
# ==========================================

print("Upload sur YouTube...")


video_title = (
    f"{subscribers:,} Subscribers "
    f"- Hourly Update"
)


description = f"""
Current subscribers: {subscribers:,}

Gained this hour: +{gained:,}

Lost this hour: -{lost:,}

Next hour goal: {goal:,}

Road to 100,000 subscribers.

This video is automatically generated every hour.
"""


request = youtube.videos().insert(

    part="snippet,status",

    body={

        "snippet": {

            "title": video_title[:100],

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


print()
print("==============================")
print("       VIDÉO PUBLIÉE !")
print("==============================")
print(
    "https://youtube.com/watch?v="
    + response["id"]
)
print("==============================")


# ==========================================
# SAUVEGARDE DE L'HISTORIQUE
# ==========================================

history["last"] = subscribers

history_file.write_text(
    json.dumps(
        history,
        indent=2
    ),
    encoding="utf-8"
)


print()
print("Terminé !")

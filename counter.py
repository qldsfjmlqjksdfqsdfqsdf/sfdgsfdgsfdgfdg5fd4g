from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip
from pathlib import Path
import json
from datetime import datetime

# =========================
# CONNEXION YOUTUBE
# =========================

credentials = Credentials.from_authorized_user_file("token.json")

youtube = build("youtube", "v3", credentials=credentials)

data = youtube.channels().list(
    part="snippet,statistics",
    mine=True
).execute()["items"][0]

name = data["snippet"]["title"]
subscribers = int(data["statistics"]["subscriberCount"])

print("Chaîne :", name)
print("Abonnés :", subscribers)

# =========================
# HISTORIQUE
# =========================

history_file = Path("history.json")

if history_file.exists():
    history = json.loads(history_file.read_text())
else:
    history = {"last": None}

last = history["last"]

if last is None:
    gained = 0
    lost = 0
else:
    difference = subscribers - last
    gained = max(difference, 0)
    lost = max(-difference, 0)

goal = subscribers + max(gained, 1)

# =========================
# IMAGE
# =========================

W, H = 1080, 1920

image = Image.new("RGB", (W, H), (10, 12, 20))
draw = ImageDraw.Draw(image)

font_big = ImageFont.truetype(
    "C:/Windows/Fonts/arialbd.ttf", 150
)

font_medium = ImageFont.truetype(
    "C:/Windows/Fonts/arialbd.ttf", 55
)

font_small = ImageFont.truetype(
    "C:/Windows/Fonts/arial.ttf", 42
)

draw.text(
    (W//2, 250),
    name,
    font=font_medium,
    fill="white",
    anchor="mm"
)

draw.text(
    (W//2, 480),
    "SUBSCRIBERS",
    font=font_medium,
    fill="gray",
    anchor="mm"
)

draw.text(
    (W//2, 720),
    f"{subscribers:,}",
    font=font_big,
    fill="white",
    anchor="mm"
)

draw.text(
    (W//2, 980),
    f"+{gained:,} THIS HOUR",
    font=font_medium,
    fill=(80, 220, 120),
    anchor="mm"
)

draw.text(
    (W//2, 1080),
    f"-{lost:,} LOST",
    font=font_medium,
    fill=(255, 80, 80),
    anchor="mm"
)

draw.text(
    (W//2, 1280),
    "NEXT HOUR GOAL",
    font=font_small,
    fill="gray",
    anchor="mm"
)

draw.text(
    (W//2, 1370),
    f"{goal:,}",
    font=font_medium,
    fill="white",
    anchor="mm"
)

draw.text(
    (W//2, 1650),
    "ROAD TO 100,000",
    font=font_small,
    fill="gray",
    anchor="mm"
)

image.save("frame.png")

# =========================
# VIDEO
# =========================

print("Création de la vidéo...")

clip = ImageClip("frame.png").with_duration(10)

clip.write_videofile(
    "subscriber_video.mp4",
    fps=30,
    codec="libx264",
    audio=False
)

clip.close()

# =========================
# UPLOAD YOUTUBE
# =========================

print("Upload sur YouTube...")

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": f"{subscribers:,} Subscribers - Hourly Update",
            "description": (
                f"Current subscribers: {subscribers:,}\n"
                f"Gained this hour: +{gained:,}\n"
                f"Lost this hour: -{lost:,}\n"
                f"Next goal: {goal:,}"
            ),
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    },
    media_body=MediaFileUpload(
        "subscriber_video.mp4",
        mimetype="video/mp4",
        resumable=True
    )
)

response = request.execute()

print("VIDÉO PUBLIÉE !")
print("ID :", response["id"])

# =========================
# SAUVEGARDE
# =========================

history["last"] = subscribers
history_file.write_text(json.dumps(history))

print("Terminé !")
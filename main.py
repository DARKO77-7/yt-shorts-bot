import os
import openai
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# ====== CONFIGURATION ======

CHANNEL_ID = "UCDBu2oXU36JuSolLE4HsGKg"  # Your actual YouTube Channel ID
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")  # Must set in GitHub secrets

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Load API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ============================

def get_trending_topics():
    # Example topics, you can customize or fetch real trending topics
    return [
        "Shocking tech news today!",
        "Insane sports moment caught on camera",
        "AI is changing everything",
        "Gaming clip of the week",
        "Top 5 life hacks you didn’t know",
        "Unbelievable space discovery",
        "Funny TikTok trend explained",
        "New movie everyone is talking about",
        "Crazy celebrity moment",
        "Weird fact that blew my mind"
    ]

def generate_script(topic):
    prompt = f"Write a short, viral YouTube Shorts script (max 80 words) about: {topic}"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    return response.choices[0].message.content.strip()

def generate_voice(script, filename):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": script,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    with open(filename, "wb") as f:
        f.write(response.content)

def create_video(script, voice_file, video_file):
    # Placeholder: Replace with your AI video creation code or API calls
    # For now, creates an empty MP4 file (you must add video generation later)
    with open(video_file, "wb") as f:
        f.write(b"")

def get_authenticated_service():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes)
        creds = flow.run_console()
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, video_file, title, description):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["viral", "shorts"],
            "categoryId": "22"  # People & Blogs category
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
    print(f"Uploaded video id: {response['id']}")

def main():
    youtube = get_authenticated_service()
    topics = get_trending_topics()
    videos_to_post = 10  # Number of shorts to upload per run

    for i in range(videos_to_post):
        topic = topics[i % len(topics)]
        print(f"Processing topic: {topic}")

        script = generate_script(topic)
        voice_path = os.path.join(TEMP_DIR, f"voice_{i}.mp3")
        video_path = os.path.join(TEMP_DIR, f"video_{i}.mp4")

        generate_voice(script, voice_path)
        create_video(script, voice_path, video_path)
        upload_video(youtube, video_path, topic, script)

if __name__ == "__main__":
    main()

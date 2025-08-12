import os
import openai
import requests
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

# ====== API KEYS FROM GITHUB SECRETS ======
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")  # OAuth JSON

# ====== CONFIG ======
VIDEOS_PER_DAY = 10
CHANNEL_ID = "YOUR_CHANNEL_ID"  # replace
VOICE_ID = "YOUR_ELEVENLABS_VOICE_ID"
TEMP_DIR = "temp"

os.makedirs(TEMP_DIR, exist_ok=True)
openai.api_key = OPENAI_API_KEY

# ====== 1. GET TRENDING TOPICS ======
def get_trending_topics():
    # Example placeholder list - replace with real trending API if needed
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

# ====== 2. GENERATE SCRIPT ======
def generate_script(topic):
    prompt = f"Write a short, viral YouTube Shorts script (max 80 words) about: {topic}"
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    return resp.choices[0].message.content.strip()

# ====== 3. GENERATE VOICEOVER ======
def generate_voice(script, filename):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    data = {"text": script, "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}}
    r = requests.post(url, headers=headers, json=data)
    with open(filename, "wb") as f:
        f.write(r.content)

# ====== 4. CREATE VIDEO ======
def create_video(script, voice_file, video_file):
    # For now, placeholder - use Pictory API / Runway Gen-2
    with open(video_file, "wb") as f:
        f.write(b"FAKE_VIDEO_CONTENT")

# ====== 5. UPLOAD TO YOUTUBE ======
def upload_video(video_file, title, description):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": description, "tags": ["viral", "shorts"], "categoryId": "22"},
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()
    print("Uploaded:", response)

# ====== MAIN ======
def main():
    topics = get_trending_topics()
    for i in range(VIDEOS_PER_DAY):
        topic = topics[i]
        script = generate_script(topic)
        voice_path = f"{TEMP_DIR}/voice{i}.mp3"
        video_path = f"{TEMP_DIR}/video{i}.mp4"

        generate_voice(script, voice_path)
        create_video(script, voice_path, video_path)
        upload_video(video_path, topic, script)

if __name__ == "__main__":
    main()

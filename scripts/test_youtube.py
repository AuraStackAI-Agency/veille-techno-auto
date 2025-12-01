"""
Script de test pour vérifier la capacité de Qwen à résumer des vidéos YouTube
"""
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv

load_dotenv()

VIDEO_ID = "w-Ve52OmYSQ"  # N8N Tutorial
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b-instruct")

def get_transcript(video_id):
    """Récupère la transcription d'une vidéo YouTube"""
    try:
        print(f"Fetching transcript for {video_id}...")
        transcript_list = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join([t.text for t in transcript_list])
        print(f"Transcript fetched: {len(text)} characters")
        return text
    except Exception as e:
        print(f"Error: {e}")
        return None

def summarize(text):
    """Résume le texte avec Qwen"""
    prompt = f"""
    Résume cette transcription de vidéo YouTube en français.
    Concentre-toi sur les points clés.
    
    Transcription:
    {text[:5000]}
    
    Résumé (max 150 mots):
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        print(f"Sending to {OLLAMA_URL}...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '')
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print(" Starting YouTube Transcript Test")
    print("=" * 50)
    
    transcript = get_transcript(VIDEO_ID)
    if not transcript:
        print("[FAILED] Could not fetch transcript")
        exit(1)
    
    summary = summarize(transcript)
    if summary:
        print("\n" + "=" * 50)
        print("Résumé généré par Qwen:")
        print("=" * 50)
        print(summary)
        print("=" * 50)
        print("\n[SUCCESS] Test passed!")
    else:
        print("[FAILED] Could not generate summary")
        exit(1)

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import tempfile
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from google import genai
# from google.generativeai import GenerativeModel 
import whisper
from dotenv import load_dotenv
load_dotenv()

# ========== CONFIGURATION ==========

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=GEMINI_API_KEY)

# ========== MAIN FUNCTION ==========

def get_english_transcript(video_id: str) -> str:
    print(f"🟡 Trying to get English transcript for {video_id}")
    """Fetches or generates English transcript from a YouTube video."""
    try:
        # Try English transcript first
        transcript = get_transcript_in_language(video_id, "en")
        print("🟢 English transcript found.")
        return transcript

    except (TranscriptsDisabled, NoTranscriptFound):
        print("🟢 Hindi transcript found. Translating...")
        # Try fallback languages like Hindi
        try:
            raw_text = get_transcript_in_language(video_id, "hi")
            print("🔁 Hindi transcript found, translating...")
            return translate_to_english(raw_text)
        except:
            print("❌ No transcript found. Falling back to Whisper.")
            return transcribe_with_whisper(video_id)

# ========== SUBFUNCTIONS ==========

def get_transcript_in_language(video_id: str, lang_code: str) -> str:
    """Returns transcript as plain text for a specific language."""
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code])
    if not transcript_list:
        raise NoTranscriptFound(video_id)
    return " ".join(chunk['text'] for chunk in transcript_list)


def translate_to_english(text: str) -> str:
    """Uses Gemini to translate non-English text into English."""
    try:
        prompt = f"Translate the following Hindi text to English:\n\n{text}"
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Translate the following Hindi text to English:\n\n{text}"
        )
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini translation failed:", str(e))
        return ""

def transcribe_with_whisper(video_id: str) -> str:
    """Downloads audio via yt-dlp and transcribes using Whisper."""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "audio.mp3")
            download_audio(video_id, output_path)
            print("🔊 Audio downloaded. Transcribing with Whisper...")
            model = whisper.load_model("base")  # Consider "small" for better accuracy
            result = model.transcribe(output_path)
            return result["text"]
    except Exception as e:
        print("❌ Whisper transcription failed:", str(e))
        return ""
    

def download_audio(video_id: str, output_path: str):
    """Downloads audio from a YouTube video using yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", output_path,
        url
    ]
    subprocess.run(cmd, check=True)

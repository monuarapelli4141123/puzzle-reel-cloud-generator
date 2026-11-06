import os
import asyncio
import subprocess
import edge_tts
from huggingface_hub import HfApi

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_REPO = os.environ.get("HF_REPO", "dreamersvizon/daily-reels-vault")

IMAGE_PATH = "puzzle_image.jpg"
VOICE_PATH = "voice.mp3"
OUTPUT_VIDEO = "github_actions_puzzle_reel.mp4"

TTS_TEXT = os.environ.get(
    "TTS_TEXT",
    "Can you spot the odd one out? Time is ticking! Five, four, three, two, one... Time is up! Look right there!"
)

async def synthesize_voice():
    print("🎙️ Synthesizing voice with Edge-TTS (Free Microsoft Neural)...")
    communicate = edge_tts.Communicate(TTS_TEXT, "en-US-AnaNeural")
    await communicate.save(VOICE_PATH)
    print("✅ Voiceover generated.")

def render_reel():
    print("🎬 Rendering 1080x1920 9:16 Reel with CPU FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", IMAGE_PATH,
        "-i", VOICE_PATH,
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
        "drawbox=x=80:y=1800:w='max(0, 920*(1-(t/11)))':h=24:color=red@0.9:t=fill[v_bar];"
        "[v_bar]drawbox=enable='between(t,11,14)':x=400:y=700:w=260:h=260:color=yellow@0.9:t=10[v_final]",
        "-map", "[v_final]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac",
        "-t", "14",
        "-pix_fmt", "yuv420p",
        OUTPUT_VIDEO
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print("✅ Reel rendered:", OUTPUT_VIDEO)

def upload_to_hf():
    if not HF_TOKEN:
        print("⚠️ No HF_TOKEN provided, skipping upload.")
        return
    print("☁️ Uploading to Hugging Face Vault...")
    api = HfApi(token=HF_TOKEN)
    api.create_repo(repo_id=HF_REPO, repo_type="dataset", exist_ok=True)
    api.upload_file(
        path_or_fileobj=OUTPUT_VIDEO,
        path_in_repo=f"github_actions/{OUTPUT_VIDEO}",
        repo_id=HF_REPO,
        repo_type="dataset"
    )
    print(f"🎉 Stored at: https://huggingface.co/datasets/{HF_REPO}")

if __name__ == "__main__":
    asyncio.run(synthesize_voice())
    render_reel()
    upload_to_hf()

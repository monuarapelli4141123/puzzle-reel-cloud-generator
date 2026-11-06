import os
import asyncio
import subprocess
import edge_tts
from huggingface_hub import HfApi

# 1. Generate the Authentic Puzzle Grid Image
import create_puzzle_grid
target_box = create_puzzle_grid.make_puzzle_base()
tx, ty, tw, th = target_box # (572, 860, 190, 210)

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_REPO = os.environ.get("HF_REPO", "dreamersvizon/daily-reels-vault")

IMAGE_PATH = "real_puzzle_image.jpg"
VOICE_PATH = "puzzle_voice.mp3"
OUTPUT_VIDEO = "real_odd_one_out_reel.mp4"

# 2. Authentic Engaging Script
TTS_TEXT = (
    "Can you spot the winking bear? "
    "Look closely at their eyes! "
    "Five, four, three, two, one... "
    "Time is up! Look right there, he's winking!"
)

async def synthesize_voice():
    print("🎙️ Synthesizing voiceover with Edge-TTS...")
    communicate = edge_tts.Communicate(TTS_TEXT, "en-US-AnaNeural")
    await communicate.save(VOICE_PATH)
    print("✅ Voiceover generated.")

def render_reel():
    print("🎬 Rendering authentic 1080x1920 Puzzle Reel with Countdown Bar & Reveal...")
    # Add a shrinking countdown bar along the bottom from t=3 to t=11
    # Highlight the exact winking bear box at (tx, ty, tw, th) with flashing golden circle from t=11 to 14
    cx = tx + tw // 2
    cy = ty + th // 2
    r = tw // 2 + 15

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", IMAGE_PATH,
        "-i", VOICE_PATH,
        "-filter_complex",
        # Countdown bar at the bottom (x=80, y=1770, w=920 shrinking over 11s)
        f"[0:v]drawbox=x=80:y=1770:w='max(0, 920*(1-(t/11)))':h=28:color=red@0.95:t=fill[v_bar];"
        # Golden animated highlight circle/box precisely enclosing the winking bear from t=11 to t=14
        f"[v_bar]drawbox=enable='between(t,11,14)':x={tx-10}:y={ty-10}:w={tw+20}:h={th+20}:color=yellow@0.95:t=10[v_final]",
        "-map", "[v_final]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac",
        "-t", "14",
        "-pix_fmt", "yuv420p",
        OUTPUT_VIDEO
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print("✅ Authentic Reel rendered successfully:", OUTPUT_VIDEO)

def upload_to_hf():
    if not HF_TOKEN:
        print("⚠️ No HF_TOKEN provided, skipping upload.")
        return
    print("☁️ Uploading authentic puzzle reel to Hugging Face...")
    api = HfApi(token=HF_TOKEN)
    api.create_repo(repo_id=HF_REPO, repo_type="dataset", exist_ok=True)
    api.upload_file(
        path_or_fileobj=OUTPUT_VIDEO,
        path_in_repo=f"authentic_puzzles/{OUTPUT_VIDEO}",
        repo_id=HF_REPO,
        repo_type="dataset"
    )
    print(f"🎉 Stored at: https://huggingface.co/datasets/{HF_REPO}")

if __name__ == "__main__":
    asyncio.run(synthesize_voice())
    render_reel()
    upload_to_hf()

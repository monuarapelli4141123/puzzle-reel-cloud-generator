import os
import asyncio
import subprocess
import numpy as np
import wave
import edge_tts
from huggingface_hub import HfApi

import create_puzzle_grid
target_box = create_puzzle_grid.make_puzzle_base()
tx, ty, tw, th = target_box

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_REPO = os.environ.get("HF_REPO", "dreamersvizon/daily-reels-vault")

IMAGE_PATH = "real_puzzle_image.jpg"
VOICE_PATH = "voice_track.mp3"
BGM_PATH = "custom_puzzle_bgm.wav"
OUTPUT_VIDEO = "upgraded_puzzle_reel.mp4"

# 1. High-Energy Script with Natural Pacing
TTS_TEXT = (
    "Can you spot the winking bear? "
    "Check their eyes closely! "
    "Five, four, three, two, one... "
    "Time is up! Look right there, he's winking!"
)

# 2. Synthesize High-Energy Humanlike Voice (en-US-AvaNeural / en-US-AndrewMultilingualNeural)
# +5% pitch and +10% rate for energetic, captivating game show host pacing
async def synthesize_voice():
    print("🎙️ Synthesizing dynamic voiceover with Edge-TTS (Ava / High-Energy)...")
    # Ava is warm, natural, and expressive for all age groups
    communicate = edge_tts.Communicate(
        text=TTS_TEXT,
        voice="en-US-AvaNeural",
        rate="+8%",
        pitch="+4Hz"
    )
    await communicate.save(VOICE_PATH)
    print("✅ Voiceover generated.")

# 3. Synthesize 100% Royalty-Free Suspense Background Music + Ticking + Chime
def generate_bgm():
    print("🎵 Synthesizing custom suspense Lo-Fi BGM with ticking clock & victory chime...")
    sample_rate = 44100
    duration = 14.0
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # A. Warm bouncy Lo-Fi synth chord progression
    bass_freqs = [130.81, 110.00, 146.83, 98.00]
    melody = np.zeros(n_samples)
    for i in range(14):
        freq = bass_freqs[i % 4]
        t_sec = t[(t >= i) & (t < i + 1)] - i
        env = np.exp(-1.5 * t_sec)
        chord = (np.sin(2 * np.pi * freq * t_sec) + 
                 0.5 * np.sin(2 * np.pi * freq * 1.5 * t_sec) + 
                 0.3 * np.sin(2 * np.pi * freq * 2.0 * t_sec)) * env
        melody[(t >= i) & (t < i + 1)] += chord

    # B. Rhythmic countdown clock ticks (t=3 to t=11)
    ticks = np.zeros(n_samples)
    for sec in range(3, 11):
        tick_start = int(sec * sample_rate)
        tick_len = int(0.08 * sample_rate)
        t_tick = np.linspace(0, 0.08, tick_len, endpoint=False)
        tick_sound = np.sin(2 * np.pi * 800 * t_tick) * np.exp(-45 * t_tick)
        ticks[tick_start : tick_start + tick_len] += tick_sound * 0.9

    # C. Victory Bell Chime at Reveal (t=11)
    chime = np.zeros(n_samples)
    chime_start = int(11.0 * sample_rate)
    chime_len = int(2.5 * sample_rate)
    t_chime = np.linspace(0, 2.5, chime_len, endpoint=False)
    bell = (np.sin(2 * np.pi * 1046 * t_chime) +
            np.sin(2 * np.pi * 1318 * t_chime) +
            np.sin(2 * np.pi * 1568 * t_chime) +
            0.5 * np.sin(2 * np.pi * 2093 * t_chime)) * np.exp(-2.2 * t_chime)
    chime[chime_start : chime_start + chime_len] += bell * 0.7

    # Mix: Lo-fi music + countdown ticks + win chime
    bg_music = melody * 0.12 + ticks + chime
    bg_music = np.clip(bg_music, -0.95, 0.95)

    with wave.open(BGM_PATH, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes((bg_music * 32767).astype(np.int16).tobytes())
    print("✅ BGM & SFX ready.")

# 4. Render 1080x1920 Video with Audio Mixing (Voice + Ducked BGM)
def render_reel():
    print("🎬 Rendering Upgraded Puzzle Reel with Multi-Track Audio Mixing...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", IMAGE_PATH,
        "-i", VOICE_PATH,
        "-i", BGM_PATH,
        "-filter_complex",
        # Visual countdown bar + golden answer frame
        f"[0:v]drawbox=x=80:y=1770:w='max(0, 920*(1-(t/11)))':h=28:color=red@0.95:t=fill[v_bar];"
        f"[v_bar]drawbox=enable='between(t,11,14)':x={tx-10}:y={ty-10}:w={tw+20}:h={th+20}:color=yellow@0.95:t=10[v_final];"
        # Audio Mix: Voice at 100% volume, Background Music at 45% so voice is crystal clear
        "[1:a]volume=1.0[a_voice];"
        "[2:a]volume=0.45[a_bgm];"
        "[a_voice][a_bgm]amix=inputs=2:duration=first:dropout_transition=2[a_final]",
        "-map", "[v_final]",
        "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "14",
        "-pix_fmt", "yuv420p",
        OUTPUT_VIDEO
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print("✅ Upgraded Reel rendered:", OUTPUT_VIDEO)

def upload_to_hf():
    if not HF_TOKEN:
        print("⚠️ No HF_TOKEN provided, skipping upload.")
        return
    print("☁️ Uploading upgraded puzzle reel to Hugging Face...")
    api = HfApi(token=HF_TOKEN)
    api.create_repo(repo_id=HF_REPO, repo_type="dataset", exist_ok=True)
    api.upload_file(
        path_or_fileobj=OUTPUT_VIDEO,
        path_in_repo=f"upgraded_reels/{OUTPUT_VIDEO}",
        repo_id=HF_REPO,
        repo_type="dataset"
    )
    print(f"🎉 Stored at: https://huggingface.co/datasets/{HF_REPO}")

if __name__ == "__main__":
    asyncio.run(synthesize_voice())
    generate_bgm()
    render_reel()
    upload_to_hf()

# Video Enhancer

A local, budget-friendly alternative to Trupeer AI. Upload a video, transcribe and clean up the narration, re-voice with natural AI TTS, add captions, and download the final video. Costs ~$0.20 per video via OpenAI APIs.

## What it does

1. You upload a video through a web UI
2. Audio is extracted and transcribed using OpenAI Whisper
3. The transcript is cleaned up by GPT-4o-mini (removes filler words, fixes grammar)
4. You edit the script in a timestamped editor synced to the original video
5. You pick an AI voice and click Generate
6. OpenAI TTS generates the new voiceover
7. FFmpeg combines the original video + new audio + burned-in captions
8. You preview and download the final video

## Setup (Docker — recommended)

### Prerequisites

- **Docker Desktop** — download from https://www.docker.com/products/docker-desktop/
- **OpenAI API key** — get one at https://platform.openai.com/api-keys

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/mpalmi3/video-enhancer.git
cd video-enhancer

# 2. Create your .env file with your OpenAI API key
cp .env.example .env
# Open .env in a text editor and replace "your-key-here" with your actual API key

# 3. Build and run
docker compose up --build

# 4. Open in your browser
# http://localhost:8000
```

To stop the server, press `Ctrl+C` in the terminal or run `docker compose down`.

## Setup (without Docker)

### Prerequisites

- **Python 3.10+** — https://www.python.org/downloads/
- **FFmpeg** — must be on your system PATH
  - Windows: `winget install FFmpeg`
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **OpenAI API key**

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/mpalmi3/video-enhancer.git
cd video-enhancer

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env
# Open .env and replace "your-key-here" with your actual API key

# 4. Run the server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 5. Open in your browser
# http://localhost:8000
```

## Cost per video (5–8 minutes)

| Service | Cost |
|---------|------|
| Whisper transcription | ~$0.05 |
| GPT-4o-mini cleanup | ~$0.01 |
| OpenAI TTS | ~$0.10 |
| **Total** | **~$0.16–$0.25** |

## Available voices

| Voice | Description |
|-------|-------------|
| alloy | Neutral & balanced |
| echo | Warm & smooth |
| fable | Expressive & British |
| onyx | Deep & authoritative |
| nova | Friendly & upbeat |
| shimmer | Clear & gentle |

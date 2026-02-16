import os
import subprocess
import tempfile
from openai import OpenAI

VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
MAX_CHARS = 4096


def generate_voiceover(script_text: str, voice: str, output_path: str) -> str:
    """Generate TTS audio from script using OpenAI TTS API.

    Splits long scripts into chunks under the 4096-char limit,
    generates audio for each chunk, then concatenates them.
    """
    if voice not in VOICES:
        raise ValueError(f"Voice must be one of: {VOICES}")

    client = OpenAI()
    chunks = _split_text(script_text, MAX_CHARS)

    if len(chunks) == 1:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=chunks[0],
        )
        response.stream_to_file(output_path)
        return output_path

    # Multiple chunks: generate each, then concatenate with FFmpeg
    chunk_files = []
    try:
        for i, chunk in enumerate(chunks):
            chunk_path = output_path.replace(".mp3", f"_chunk{i}.mp3")
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=chunk,
            )
            response.stream_to_file(chunk_path)
            chunk_files.append(chunk_path)

        _concatenate_audio(chunk_files, output_path)
    finally:
        for f in chunk_files:
            if os.path.exists(f):
                os.remove(f)

    return output_path


def _split_text(text: str, max_chars: int) -> list[str]:
    """Split text into chunks at sentence boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""

    sentences = text.replace(". ", ".|").replace("? ", "?|").replace("! ", "!|").split("|")

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = (current + " " + sentence).strip()
        else:
            if current:
                chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)

    return chunks


def _concatenate_audio(chunk_files: list[str], output_path: str) -> None:
    """Concatenate multiple audio files using FFmpeg."""
    list_file = output_path.replace(".mp3", "_filelist.txt")
    try:
        with open(list_file, "w") as f:
            for chunk_path in chunk_files:
                safe_path = chunk_path.replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                output_path,
            ],
            check=True,
            capture_output=True,
        )
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)

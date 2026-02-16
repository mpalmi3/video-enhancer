from app.services.video import get_audio_duration


def generate_srt(segments: list[dict], output_path: str, tts_audio_path: str | None = None, original_duration: float | None = None) -> str:
    """Generate SRT caption file from segments.

    If tts_audio_path is provided, scales timings to match the TTS audio duration
    relative to the original video duration.
    """
    if tts_audio_path and original_duration:
        tts_duration = get_audio_duration(tts_audio_path)
        if original_duration > 0:
            scale = tts_duration / original_duration
        else:
            scale = 1.0
    else:
        scale = 1.0

    with open(output_path, "w", encoding="utf-8") as f:
        index = 1
        for seg in segments:
            start = seg["start"] * scale
            end = seg["end"] * scale
            text = seg["text"].strip()
            if not text:
                continue

            f.write(f"{index}\n")
            f.write(f"{_format_timestamp(start)} --> {_format_timestamp(end)}\n")
            f.write(f"{text}\n\n")
            index += 1

    return output_path


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

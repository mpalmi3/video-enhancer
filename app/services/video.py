import subprocess
import os


def extract_audio(video_path: str) -> str:
    """Extract audio from video as WAV using FFmpeg."""
    audio_path = os.path.splitext(video_path)[0] + "_audio.wav"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            audio_path,
        ],
        check=True,
        capture_output=True,
    )
    return audio_path


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using FFprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using FFprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def assemble_video(
    video_path: str,
    audio_path: str,
    srt_path: str,
    output_path: str,
) -> str:
    """Combine original video (muted) + new audio + captions in a black bar below the video."""
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")

    # Pad 80px black bar at the bottom, then render captions into that bar
    video_filter = (
        f"pad=iw:ih+80:0:0:black,"
        f"subtitles='{srt_escaped}':force_style="
        "'FontSize=14,FontName=Arial,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,Outline=1,Shadow=0,"
        "MarginV=20,Alignment=2'"
    )

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-vf", video_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path,
        ],
        check=True,
        capture_output=True,
    )
    return output_path

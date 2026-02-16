from openai import OpenAI


def transcribe(audio_path: str) -> dict:
    """Transcribe audio using OpenAI Whisper API with word-level timestamps.

    Returns:
        {
            "text": "full transcript text",
            "segments": [{"start": 0.0, "end": 2.5, "text": "Hello world"}, ...]
        }
    """
    client = OpenAI()

    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    segments = []
    for seg in response.segments:
        segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
        })

    return {
        "text": response.text,
        "segments": segments,
    }

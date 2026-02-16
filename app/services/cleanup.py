import json
from openai import OpenAI


CLEANUP_PROMPT = """You are a script editor. Clean up this video narration transcript.

Rules:
- Remove filler words: um, uh, like, you know, so basically, I mean, right, actually, sort of, kind of
- Fix grammar and awkward phrasing
- Keep the meaning and tone identical
- Do NOT add new content or change the message
- Keep it natural and conversational

Input is a JSON array of segments with start/end times and text.
Return a JSON object with:
- "cleaned_text": the full cleaned script as a single string
- "segments": array of objects with "start", "end", "text" (cleaned text for each segment, preserving original timing)

If two adjacent segments merge into one after cleanup, keep the start of the first and end of the last.
Remove any segments that become empty after filler removal.

Return ONLY valid JSON, no markdown formatting."""


def cleanup_script(raw_transcript: str, segments: list[dict]) -> dict:
    """Clean up transcript using GPT-4o-mini.

    Returns:
        {
            "cleaned_text": "full cleaned script",
            "segments": [{"start": 0.0, "end": 2.5, "text": "cleaned text"}, ...]
        }
    """
    client = OpenAI()

    input_data = json.dumps(segments, indent=2)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CLEANUP_PROMPT},
            {"role": "user", "content": input_data},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result

import json
from typing import Any, Dict

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

SYSTEM_PROMPT = """
You are an AI news extraction agent.

Given a transcript of a short video, you must:
1. Decide if it is NEWS or NOT.
2. If it is news, write:
   - A short, neutral, factual headline (<= 15 words)
   - A short, neutral summary (<= 50 words)
   - A main category, e.g. politics, economy, business, tech, sports, entertainment, world, disaster, celebrity, misc.
   - A small list of hashtag-style tags (e.g. ["#Breaking", "#India", "#Elections"])

Rules:
- Be strictly factual, no opinions, no hype.
- If the video is not news, mark it clearly as not news.
- Never include emojis.
- Always respond in valid JSON only, with this schema:

{
  "is_news": true/false,
  "category": "string or null",
  "headline": "string or null",
  "summary": "string or null",
  "tags": ["#tag1", "#tag2", ...]
}
""".strip()


def analyze_transcript(transcript: str) -> Dict[str, Any]:
    """
    Call the LLM to classify & summarize a transcript.
    """
    user_prompt = f"""
Transcript:
\"\"\"{transcript.strip()}\"\"\"

Return JSON only. Do not add explanations.
""".strip()

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = content[start : end + 1]
            data = json.loads(json_str)
        else:
            raise ValueError(f"LLM did not return valid JSON: {content}")

    data.setdefault("is_news", False)
    data.setdefault("category", None)
    data.setdefault("headline", None)
    data.setdefault("summary", None)
    data.setdefault("tags", [])

    tags = data.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    elif isinstance(tags, list):
        tags = [str(t).strip() for t in tags if str(t).strip()]
    data["tags"] = tags

    return data


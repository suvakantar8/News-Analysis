import os

# ─────────────────────────────────────────────
# LLM CONFIG (OpenAI-compatible, e.g. Groq/OpenRouter)
# ─────────────────────────────────────────────
# For Groq:
#   export OPENAI_BASE_URL="https://api.groq.com/openai/v1"
#   export OPENAI_API_KEY="your_groq_api_key"
# For OpenRouter:
#   export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
#   export OPENAI_API_KEY="your_openrouter_api_key"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")  # default, can be overridden


# ─────────────────────────────────────────────
# YT-DLP / AUDIO CONFIG
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YTDLP_DOWNLOAD_DIR = os.getenv(
    "YTDLP_DOWNLOAD_DIR",
    os.path.join(BASE_DIR, "downloads"),
)

os.makedirs(YTDLP_DOWNLOAD_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# WHISPER CONFIG
# ─────────────────────────────────────────────
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "tiny")  # "tiny", "base", "small", ...



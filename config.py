import os
from dotenv import load_dotenv

load_dotenv()

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemma3:latest")

# SEO Analysis Settings
MAX_CONTENT_LENGTH = 10000
REQUEST_TIMEOUT = 30
USER_AGENT = "SEO-Analyzer-Bot/1.0"

# Agent Settings
AGENT_TEMPERATURE = 0.1
MAX_TOKENS = 4000
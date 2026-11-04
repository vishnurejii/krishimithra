"""
Core configuration for KrishiMitra AI platform.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_lpZLi1DFq2sg@ep-aged-river-bcylj3c7-pooler.c-16.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# AI / LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# Crawler settings
CRAWLER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 "
    "KrishiMitraGovCrawler/1.0 (+https://github.com/krishimitra-ai)"
)
CRAWLER_TIMEOUT_SECONDS = int(os.getenv("CRAWLER_TIMEOUT_SECONDS", "20"))
CRAWLER_POLITENESS_DELAY = float(os.getenv("CRAWLER_POLITENESS_DELAY", "1.5"))
CRAWLER_MAX_RETRIES = int(os.getenv("CRAWLER_MAX_RETRIES", "3"))

# Storage settings
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", str(BASE_DIR / "storage" / "documents")))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Logs
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

"""Application configuration loader."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centralized configuration from environment variables."""

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "chroma_db")

    # Supported sports and their search keywords
    SPORTS = [
        {"id": "cricket", "name": "Cricket", "icon": "🏏"},
        {"id": "football", "name": "Football (Soccer)", "icon": "⚽"},
        {"id": "basketball", "name": "Basketball", "icon": "🏀"},
        {"id": "tennis", "name": "Tennis", "icon": "🎾"},
        {"id": "baseball", "name": "Baseball", "icon": "⚾"},
        {"id": "f1", "name": "Formula 1", "icon": "🏎️"},
        {"id": "olympics", "name": "Olympics", "icon": "🏅"},
    ]

    DIFFICULTIES = ["easy", "medium", "hard"]

    @classmethod
    def validate(cls):
        """Ensure required keys are present."""
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Please set them in the .env file."
            )

# Core configuration for the DyslexiQuest backend

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    api_host: str = "localhost"
    api_port: int = 8000
    log_level: str = "info"
    
    # CORS Settings
    cors_origins: List[str] = [
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:3001", "http://127.0.0.1:3001"
    ]
    
    # Gemini API Settings
    gemini_api_key: str = ""
    
    # Game Settings
    max_sessions: int = 1000
    session_timeout_minutes: int = 60
    max_turns_per_game: int = 10
    max_backtrack_count: int = 2
    
    # Rate Limiting
    rate_limit_per_minute: int = 30
    
    # Content Safety
    enable_content_filter: bool = True
    max_response_length: int = 300
    min_response_length: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Game configuration constants
GAME_CONFIG = {
    "MAX_TURNS": settings.max_turns_per_game,
    "MAX_BACKTRACK": settings.max_backtrack_count,
    "RESPONSE_MAX_LENGTH": settings.max_response_length,
    "RESPONSE_MIN_LENGTH": settings.min_response_length,
    "SESSION_TIMEOUT": settings.session_timeout_minutes * 60,  # Convert to seconds
}

# Genre-specific prompts and settings
GENRE_SETTINGS = {
    "fantasy": {
        "name": "Fantasy Adventure",
        "themes": ["magic", "wizards", "dragons", "enchanted forests", "castles"],
        "vocabulary_categories": ["magic", "characters", "places", "objects"]
    },
    "adventure": {
        "name": "Treasure Hunt Adventure", 
        "themes": ["exploration", "treasure hunting", "ancient ruins", "maps"],
        "vocabulary_categories": ["action", "objects", "places", "general"]
    },
    "mystery": {
        "name": "Mystery Detective",
        "themes": ["puzzles", "clues", "solving mysteries", "investigation"],
        "vocabulary_categories": ["puzzle", "general", "action", "descriptive"]
    },
    "sci-fi": {
        "name": "Space Explorer",
        "themes": ["space travel", "alien worlds", "technology", "exploration"],
        "vocabulary_categories": ["general", "action", "descriptive", "places"]
    }
}

# Content filtering keywords (inappropriate content to avoid)
CONTENT_FILTER_KEYWORDS = [
    "violence", "weapon", "fight", "battle", "war", "death", "kill",
    "scary", "horror", "frightening", "terrifying", "nightmare",
    "dark", "evil", "monster", "demon", "ghost", "zombie",
]

# Fallback responses for various situations
FALLBACK_RESPONSES = {
    "api_error": "The magical storytelling crystal is having trouble connecting. Let me try to continue your adventure with what I remember...",
    "content_filter": "Let's keep our adventure friendly and fun! Try a different approach to continue your story.",
    "invalid_input": "I didn't quite understand that. Could you try describing what you want to do in a different way?",
    "session_expired": "It looks like your adventure session has expired. Would you like to start a new adventure?",
    "max_turns": "What an incredible adventure you've had! You've reached the end of this story, but there are many more adventures waiting for you!",
}

def get_environment_info() -> dict:
    """Get current environment information for debugging"""
    return {
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "log_level": settings.log_level,
        "has_gemini_key": bool(settings.gemini_api_key),
        "max_sessions": settings.max_sessions,
        "cors_origins": settings.cors_origins,
    }

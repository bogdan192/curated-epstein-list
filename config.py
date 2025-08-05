"""Configuration management for the Epstein List project."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
    
    # Output settings
    OUTPUT_DIRECTORY = Path(os.getenv('OUTPUT_DIRECTORY', 'output'))
    DEFAULT_OUTPUT_FILE = os.getenv('DEFAULT_OUTPUT_FILE', 'extracted_names.xlsx')
    
    # Processing settings
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
    REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.0'))
    
    # Ensure output directory exists
    OUTPUT_DIRECTORY.mkdir(exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append('OPENAI_API_KEY')
        
        if missing:
            print(f"Warning: Missing API keys: {', '.join(missing)}")
            print("Some functionality may be limited. Please set these in your .env file.")
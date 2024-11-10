import json
import logging
import os
from typing import Dict, Any

def setup_logging() -> logging.Logger:
    """Configure and return logger"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load and parse JSON file"""
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {filepath}")
        raise

def save_json_file(filepath: str, data: Dict[str, Any]) -> None:
    """Save data to JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"Failed to save file {filepath}: {str(e)}")
        raise

def detect_language(text: str) -> str:
    """
    Detect if text is primarily Arabic or English.
    Uses Unicode ranges to properly detect Arabic text.
    """
    arabic_count = 0
    english_count = 0
    
    for char in text:
        # Arabic Unicode ranges
        if '\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F' or '\uFB50' <= char <= '\uFDFF' or '\uFE70' <= char <= '\uFEFF':
            arabic_count += 1
        # Basic Latin (English) range
        elif '\u0020' <= char <= '\u007F':
            english_count += 1
    
    # If text has more Arabic characters, consider it Arabic
    return 'ar' if arabic_count > english_count else 'en'

def load_env_var(key: str, default: str = None) -> str:
    """
    Load environment variable with error handling.
    Raises ValueError if required variable is missing.
    """
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

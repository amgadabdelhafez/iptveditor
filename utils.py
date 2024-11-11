import json
import logging
import os
from typing import Dict, Any
from logging.handlers import MemoryHandler

class MinimalFormatter(logging.Formatter):
    """Custom formatter that only shows the message for INFO level"""
    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        return super().format(record)

class SummaryHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.shows_processed = 0
        self.shows_failed = 0
        self.current_show = None
    
    def emit(self, record):
        if "Processing shows" in record.msg:
            return  # Skip batch processing messages in summary
        if record.levelno == logging.INFO:
            if "✗" in record.msg:
                self.shows_processed += 1
                self.shows_failed += 1
            elif "✓" in record.msg:
                self.shows_processed += 1
    
    def get_summary(self):
        if self.shows_processed == 0:
            return None
            
        success_count = self.shows_processed - self.shows_failed
        success_rate = (success_count / self.shows_processed * 100) if self.shows_processed > 0 else 0
        
        # Create visual bar for success rate
        bar_length = 20
        filled_length = int(bar_length * success_rate / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        return f"""
╔══════════════ Processing Summary ══════════════╗
║                                               ║
║  Total Processed: {self.shows_processed:4d}                        ║
║  ✓ Successful:    {success_count:4d}                        ║
║  ✗ Failed:        {self.shows_failed:4d}                        ║
║                                               ║
║  Success Rate: {success_rate:6.1f}%                        ║
║  [{bar}] {success_rate:5.1f}%  ║
║                                               ║
╚═══════════════════════════════════════════════╝"""

def setup_logging() -> logging.Logger:
    """Configure and return logger with file and console handlers"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler('logs/detailed.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Console handler for minimal progress only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(MinimalFormatter())
    
    # Summary handler
    summary_handler = SummaryHandler()
    summary_handler.setLevel(logging.INFO)
    
    # Add all handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(summary_handler)
    
    return logger

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

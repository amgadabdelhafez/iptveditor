# IPTV Editor

A Python tool for managing and updating IPTV show information using TMDB data. Features intelligent caching, Arabic/English language support, and batch processing capabilities.

## Features

- TMDB show information lookup and matching
- Support for both Arabic and English show titles
- Smart language detection and matching
- Comprehensive caching system
- Batch processing with state management
- Detailed logging and error handling

## Requirements

- Python 3.6+
- Virtual environment (recommended)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd iptveditor
```

2. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file with your API keys:

```bash
TMDB_API_KEY=your_tmdb_api_key
IPTVEDITOR_TOKEN=your_iptveditor_token
```

## Usage

### Command Line Arguments

- `--local`: Use local JSON files instead of API
- `--batch-size`: Number of shows to process in one run (default: 10)

### Examples

Process shows using API:

```bash
python3 main.py
```

Process shows using local JSON files:

```bash
python3 main.py --local
```

Process specific number of shows:

```bash
python3 main.py --batch-size 5
```

## Implementation Details

### Project Structure

```
iptveditor/
├── main.py              # Entry point and CLI handling
├── editor.py            # Core IPTVEditor class
├── api.py              # API clients (TMDB & IPTV Editor)
├── config.py           # Configuration and constants
├── utils.py            # Helper functions
├── database.py         # SQLite cache implementation
├── .env               # Environment variables
└── requirements.txt   # Dependencies
```

### Caching System

The project uses SQLite with SQLAlchemy for efficient caching of API responses:

#### Database Schema

1. TMDB Search Cache:

```sql
CREATE TABLE tmdb_search_cache (
    id INTEGER PRIMARY KEY,
    query VARCHAR(255) NOT NULL,
    response TEXT NOT NULL,  -- JSON string
    created_at DATETIME,
    updated_at DATETIME
);
```

- Caches show search results
- Includes "not found" results to prevent redundant searches
- Indexed by show name for fast lookups

2. TMDB Details Cache:

```sql
CREATE TABLE tmdb_details_cache (
    id INTEGER PRIMARY KEY,
    tmdb_id INTEGER UNIQUE NOT NULL,
    response TEXT NOT NULL,  -- JSON string
    created_at DATETIME,
    updated_at DATETIME
);
```

- Stores detailed show information
- Indexed by TMDB ID

3. Episodes Cache:

```sql
CREATE TABLE iptveditor_episodes_cache (
    id INTEGER PRIMARY KEY,
    show_id INTEGER UNIQUE NOT NULL,
    response TEXT NOT NULL,  -- JSON string
    created_at DATETIME,
    updated_at DATETIME
);
```

- Caches show episodes
- Indexed by show ID

4. Update Cache:

```sql
CREATE TABLE iptveditor_update_cache (
    id INTEGER PRIMARY KEY,
    show_id INTEGER NOT NULL,
    tmdb_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    response TEXT NOT NULL,  -- JSON string
    created_at DATETIME,
    updated_at DATETIME
);
```

- Caches show update responses
- Composite index on (show_id, tmdb_id, category_id)

### Cache Features

1. Not Found Handling:

- Caches negative search results
- Prevents redundant API calls for known missing shows
- Special response format for not found cases:

```python
{
    "not_found": True,
    "reason": "No results found in TMDB"
}
```

2. Language Support:

- Smart language detection using Unicode ranges
- Prioritizes exact title matches
- Falls back to language-based matches
- Configurable fallback to first result

3. Performance:

- Indexed queries for fast lookups
- Automatic cache updates
- Cache hit/miss statistics tracking
- Timestamp tracking for cache entries

### State Management

- Tracks progress through show processing
- Resumes from last processed show
- Persists state between runs
- Handles failures gracefully

### Error Handling

- Comprehensive error logging
- Graceful failure recovery
- Detailed progress tracking
- Cache statistics reporting

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# IPTV Editor

A Python tool for managing and updating IPTV show information using TMDB data. Features intelligent caching, Arabic/English language support, and batch processing capabilities.

## Features

- TMDB show information lookup and matching
- Support for both Arabic and English show titles with automatic language detection
- Intelligent transliteration for Arabic titles using Buckwalter transliteration
- Comprehensive SQLite-based caching system with hit rate tracking
- Batch processing with state management and progress tracking
- Detailed logging with both console output and file logging
- Processing summary with visual progress bars
- Automatic tracking of shows not found in TMDB

## Requirements

- Python 3.6+
- TMDB API key
- IPTV Editor token
- IPTV Editor playlist ID
- Required Python packages (see requirements.txt)

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
IPTVEDITOR_PLAYLIST_ID=your_playlist_id
```

## Usage

### Command Line Arguments

- `--batch-size`: Number of shows to process in one run (default: 10)

### Data Management

The tool intelligently manages data in the following way:

1. On first run or when JSON files are missing:

   - Fetches categories and shows from the IPTV Editor API
   - Saves data to tvshows-categories.json and tvshows-shows.json
   - Uses the fetched data for processing

2. On subsequent runs:
   - Uses existing JSON files if available
   - Only fetches from API if files are missing
   - Maintains data consistency across runs

This approach ensures:

- Efficient use of API resources
- Consistent data between sessions
- Quick startup when data is already available
- Automatic recovery if files are missing

### Examples

Process shows with default batch size:

```bash
python3 main.py
```

Process specific number of shows:

```bash
python3 main.py --batch-size 5
```

## Implementation Details

### Project Structure

```
iptveditor/
├── main.py                    # Entry point and CLI handling
├── editor.py                  # Core IPTVEditor class implementation
├── api.py                     # TMDB and IPTV Editor API clients
├── config.py                  # Configuration and environment variables
├── database.py               # Cache implementation using SQLite
├── utils.py                  # Helper functions and logging setup
├── logs/                     # Directory for log files
│   └── detailed.log         # Detailed debug logs
├── not_found_shows.json     # Tracking of shows not found in TMDB
├── editor_state.json        # Processing state persistence
├── cache.db                 # SQLite cache database
├── tvshows-categories.json  # Categories data (auto-managed)
├── tvshows-shows.json      # Shows data (auto-managed)
├── .env                     # Environment variables
└── requirements.txt         # Project dependencies
```

### Caching System

The project uses SQLite for efficient caching of API responses with the following tables:

1. TMDB Search Cache:

```sql
CREATE TABLE tmdb_search_cache (
    key TEXT PRIMARY KEY,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

2. TMDB Details Cache:

```sql
CREATE TABLE tmdb_details_cache (
    key TEXT PRIMARY KEY,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

3. Episodes Cache:

```sql
CREATE TABLE episodes_cache (
    key TEXT PRIMARY KEY,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

4. Update Cache:

```sql
CREATE TABLE update_cache (
    key TEXT PRIMARY KEY,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Key Features

1. Language Support:

- Automatic language detection using Unicode ranges
- Arabic to English transliteration using Buckwalter system
- Fallback search strategies for better matching

2. State Management:

- Persistent processing state across runs
- Category-based processing with resumption
- Batch size control for processing chunks
- Progress tracking per category

3. Error Handling & Logging:

- Comprehensive error logging to file
- Console progress indicators (✓/✗)
- Visual processing summary with statistics
- Cache hit/miss rate tracking
- Automatic tracking of not found shows

4. Cache Management:

- SQLite-based persistent caching
- Automatic cache creation and updates
- Hit rate statistics tracking
- Separate tables for different types of data
- JSON serialization for complex data types

### Processing Flow

1. Shows are processed by category in configurable batch sizes
2. For each show:

   - Language is detected automatically
   - TMDB search is performed with language consideration
   - For Arabic titles, transliteration is attempted if initial search fails
   - Show details and episodes are retrieved and cached
   - Updates are performed via IPTV Editor API
   - Progress is saved after each show

3. Not found shows are tracked with:

   - Original show name
   - Category information
   - Transliterated name (if applicable)
   - Any error information

4. Processing summary includes:
   - Total shows processed
   - Success/failure counts
   - Visual progress bar
   - Success rate percentage

### API Integration

The tool integrates with two main APIs:

1. TMDB API:

- Show search with language support
- Detailed show information retrieval
- Image and video metadata

2. IPTV Editor API:

- Category management (60+ categories supported)
- Show management (3,800+ shows supported)
- Episode information
- Show metadata updates

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

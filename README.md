# IPTV Editor

A Python tool for managing and updating IPTV show information using TMDB data.

## Features

- Fetch and update show information from TMDB
- Support for both Arabic and English show titles
- Batch processing with state management
- Configurable data source (API or local JSON)
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

## Project Structure

- `main.py`: Entry point and CLI handling
- `editor.py`: Core IPTVEditor class
- `api.py`: TMDB and IPTV Editor API clients
- `config.py`: Configuration and constants
- `utils.py`: Helper functions and utilities

## Features

### Language Detection

The tool uses smart language detection to properly match shows:

1. Exact title match (primary)
2. Language-based match (secondary)
3. Configurable fallback to first result

### State Management

- Automatically tracks progress
- Resumes from last processed show
- Saves state after each show

## Error Handling

- Comprehensive error logging
- Graceful failure handling
- Detailed progress tracking

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

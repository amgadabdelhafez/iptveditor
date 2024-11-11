import logging
import requests
import os
from typing import Dict, Any, List, Optional
from utils import detect_language
from database import cache_manager

class TMDBApi:
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY', 'a2764023c82b647eac48485b4deac0bf')
        self.base_url = 'https://api.themoviedb.org/3'
        self.logger = logging.getLogger(__name__)

    def search_show(self, title: str) -> Optional[Dict]:
        """Search for a TV show by title"""
        self.logger.debug(f"Searching for show: {title}")
        
        # Check cache first
        cache_key = f"tmdb_search_{title}"
        cached_result = cache_manager.get('tmdb_search', cache_key)
        if cached_result:
            self.logger.debug("Using cached search result")
            return cached_result
        
        self.logger.debug(f"No cache found, searching TMDB API for: {title}")
        
        # Detect language for better search results
        lang = detect_language(title)
        self.logger.debug(f"Detected language for '{title}': {lang}")
        
        # Search TMDB API
        params = {
            'api_key': self.api_key,
            'query': title,
            'language': f"{lang}-{'us' if lang == 'en' else lang}",
            'include_adult': True
        }
        
        response = requests.get(f"{self.base_url}/search/tv", params=params)
        results = response.json().get('results', [])
        
        if not results:
            return None
            
        # Try to find exact title match first
        for result in results:
            if result['name'].lower() == title.lower():
                self.logger.debug("Found exact title match")
                cache_manager.set('tmdb_search', cache_key, result)
                return result
        
        # Fallback to first result
        self.logger.debug(f"Found match in detected language ({lang})")
        cache_manager.set('tmdb_search', cache_key, results[0])
        return results[0]

    def get_show_details(self, tmdb_id: int) -> Dict:
        """Get detailed information for a TV show"""
        self.logger.debug(f"Getting details for TMDB ID: {tmdb_id}")
        
        # Check cache first
        cache_key = f"tmdb_details_{tmdb_id}"
        cached_result = cache_manager.get('tmdb_details', cache_key)
        if cached_result:
            self.logger.debug("Using cached show details")
            return cached_result
        
        self.logger.debug(f"No cache found, fetching details from TMDB API for ID: {tmdb_id}")
        
        # Get show details from TMDB API
        params = {
            'api_key': self.api_key,
            'language': 'en-us',
            'append_to_response': 'images,credits,videos'
        }
        
        response = requests.get(f"{self.base_url}/tv/{tmdb_id}", params=params)
        result = response.json()
        
        self.logger.debug(f"Cached details for TMDB ID {tmdb_id}")
        cache_manager.set('tmdb_details', cache_key, result)
        return result

class IPTVEditorApi:
    def __init__(self):
        self.base_url = 'https://editor.iptveditor.com'
        self.logger = logging.getLogger(__name__)

    def get_categories(self) -> List[Dict]:
        """Get all categories"""
        response = requests.get(f"{self.base_url}/api/category/get-data")
        return response.json()['items']

    def get_shows(self) -> List[Dict]:
        """Get all shows"""
        response = requests.get(f"{self.base_url}/api/stream/series/get-data")
        return response.json()['items']

    def get_episodes(self, show_id: int) -> List[Dict]:
        """Get episodes for a show"""
        self.logger.debug(f"Getting episodes for show ID: {show_id}")
        
        # Check cache first
        cache_key = f"episodes_{show_id}"
        cached_result = cache_manager.get('episodes', cache_key)
        if cached_result:
            self.logger.debug("Using cached episodes")
            return cached_result
        
        self.logger.debug(f"No cache found, fetching episodes from API for show ID: {show_id}")
        
        # Get episodes from API
        response = requests.post(
            f"{self.base_url}/api/episode/get-data",
            json={'series_id': show_id}
        )
        result = response.json()['items']
        
        self.logger.debug(f"Cached episodes for show ID {show_id}")
        cache_manager.set('episodes', cache_key, result)
        return result

    def update_show(self, show_id: int, tmdb_id: int, category_id: int) -> bool:
        """Update a show with TMDB information"""
        self.logger.debug(f"Updating show ID {show_id} with TMDB ID {tmdb_id}")
        
        # Check cache first
        cache_key = f"update_{show_id}_{tmdb_id}"
        cached_result = cache_manager.get('update', cache_key)
        if cached_result:
            self.logger.debug("Using cached update result")
            return cached_result
        
        self.logger.debug(f"No cache found, updating show via API: {show_id}")
        
        # Update show via API
        response = requests.post(
            f"{self.base_url}/api/stream/series/save",
            json={
                'id': show_id,
                'tmdb_id': tmdb_id,
                'category_id': category_id
            }
        )
        result = response.json() == 1
        
        self.logger.debug(f"Cached update result for show ID {show_id}")
        cache_manager.set('update', cache_key, result)
        return result

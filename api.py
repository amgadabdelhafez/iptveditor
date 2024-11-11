import logging
import requests
import os
from typing import Dict, Any, List, Optional
from utils import detect_language, arabic_to_english
from database import cache_manager
from config import HTTP_HEADERS, IPTVEDITOR_TOKEN, IPTVEDITOR_BASE_URL, TMDB_BASE_URL

class TMDBApi:
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY', 'a2764023c82b647eac48485b4deac0bf')
        self.base_url = TMDB_BASE_URL
        self.logger = logging.getLogger(__name__)

    def search_show(self, title: str) -> Optional[Dict]:
        """Search for a TV show by title with improved language handling"""
        self.logger.debug(f"Searching for show: {title}")
        
        # Check cache first
        cache_key = f"tmdb_search_{title}"
        cached_result = cache_manager.get('tmdb_search', cache_key)
        if cached_result:
            self.logger.debug("Using cached search result")
            return cached_result
        
        # Detect language
        lang = detect_language(title)
        self.logger.debug(f"Detected language for '{title}': {lang}")
        
        # Try with detected language first
        result = self._search_tmdb(title, lang)
        if result:
            self.logger.debug(f"Found match in {lang}")
            cache_manager.set('tmdb_search', cache_key, result)
            return result
            
        # If no results and language was Arabic, try English transliteration
        if lang == 'ar':
            transliterated = arabic_to_english(title)
            self.logger.debug(f"Trying transliterated title: {transliterated}")
            result = self._search_tmdb(transliterated, 'en')
            if result:
                self.logger.debug("Found match using transliterated title")
                cache_manager.set('tmdb_search', cache_key, result)
                return result
        
        # If still no results and language wasn't English, try English as fallback
        elif lang != 'en':
            self.logger.debug("Trying English as fallback")
            result = self._search_tmdb(title, 'en')
            if result:
                self.logger.debug("Found match in English")
                cache_manager.set('tmdb_search', cache_key, result)
                return result
        
        self.logger.debug(f"No matches found for '{title}'")
        return None

    def _search_tmdb(self, title: str, lang: str) -> Optional[Dict]:
        """Internal method to search TMDB API"""
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
                return result
        
        # Fallback to first result
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
        self.base_url = IPTVEDITOR_BASE_URL
        self.logger = logging.getLogger(__name__)
        self.headers = HTTP_HEADERS.copy()

    def get_categories(self) -> List[Dict]:
        """Get all categories"""
        response = requests.get(
            f"{self.base_url}/category/get-data",
            headers=self.headers,
            json={'token': IPTVEDITOR_TOKEN}
        )
        return response.json()['items']

    def get_shows(self) -> List[Dict]:
        """Get all shows"""
        response = requests.get(
            f"{self.base_url}/stream/series/get-data",
            headers=self.headers,
            json={'token': IPTVEDITOR_TOKEN}
        )
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
        payload = {
            'seriesId': str(show_id),
            'url': None,
            'token': IPTVEDITOR_TOKEN
        }
        
        response = requests.post(
            f"{self.base_url}/episode/get-data",
            headers=self.headers,
            json=payload
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
        
        # Update show via API with the correct payload structure
        payload = {
            'items': [{
                'id': show_id,
                'tmdb': tmdb_id,
                'youtube_trailer': '',
                'category': category_id
            }],
            'checkSaved': False,
            'token': IPTVEDITOR_TOKEN
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/stream/series/save",
                headers=self.headers,
                json=payload  # Use json parameter to properly serialize
            )
            
            # Log the full response for debugging
            self.logger.debug(f"API Response Status: {response.status_code}")
            self.logger.debug(f"API Response Headers: {response.headers}")
            self.logger.debug(f"API Response Content: {response.text}")
            
            response.raise_for_status()
            
            # Consider 200 status code and "200" response as success
            result = response.status_code == 200 and response.text.strip() == "200"
            
            self.logger.debug(f"Cached update result for show ID {show_id}")
            cache_manager.set('update', cache_key, result)
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Error response content: {e.response.text}")
            return False

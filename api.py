import logging
import requests
from typing import Dict, List, Optional

from config import (
    TMDB_API_KEY, IPTVEDITOR_TOKEN, HTTP_HEADERS,
    IPTVEDITOR_BASE_URL, TMDB_BASE_URL, FALLBACK_TO_FIRST_RESULT
)
from utils import detect_language

class TMDBApi:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def search_show(self, query: str) -> Optional[Dict]:
        """Search for show on TMDB"""
        self.logger.info(f"Searching TMDB for show: {query}")
        
        # Detect show name language
        detected_lang = detect_language(query)
        self.logger.debug(f"Detected language for '{query}': {detected_lang}")
        
        url = f"{TMDB_BASE_URL}/search/tv"
        params = {
            'language': 'en-us',
            'api_key': TMDB_API_KEY,
            'query': query,
            'include_adult': 'true'
        }
        
        try:
            response = requests.get(url, headers=HTTP_HEADERS, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data['results']:
                self.logger.warning(f"No results found for show: {query}")
                return None
            
            # Try to find exact title match first
            exact_matches = [
                result for result in data['results']
                if result.get('name', '').lower() == query.lower() or 
                   result.get('original_name', '').lower() == query.lower()
            ]
            
            if exact_matches:
                self.logger.info(f"Found exact title match for '{query}'")
                return exact_matches[0]
            
            # Then try language match
            lang_matches = [
                result for result in data['results']
                if result.get('original_language') == detected_lang
            ]
            
            if lang_matches:
                self.logger.info(f"Found match in detected language ({detected_lang})")
                return lang_matches[0]
            
            # Fall back to first result if allowed
            if FALLBACK_TO_FIRST_RESULT:
                self.logger.warning(
                    f"No matches found for '{query}' in language '{detected_lang}', "
                    "using first available result as fallback"
                )
                return data['results'][0]
            
            self.logger.error(
                f"No suitable matches found for '{query}' "
                f"(language: {detected_lang}, fallback disabled)"
            )
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"TMDB API request failed: {str(e)}")
            raise
        except (KeyError, IndexError) as e:
            self.logger.error(f"Failed to parse TMDB response: {str(e)}")
            raise

    def get_show_details(self, show_id: int) -> Dict:
        """Get detailed show information from TMDB"""
        self.logger.info(f"Getting details for TMDB ID: {show_id}")
        
        url = f"{TMDB_BASE_URL}/tv/{show_id}"
        params = {
            'language': 'en-us',
            'api_key': TMDB_API_KEY,
            'append_to_response': 'images,credits,videos'
        }
        
        try:
            response = requests.get(url, headers=HTTP_HEADERS, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get show details: {str(e)}")
            raise

class IPTVEditorApi:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_categories(self) -> List[Dict]:
        """Get categories from IPTV Editor API"""
        url = f"{IPTVEDITOR_BASE_URL}/category/series/get-data"
        payload = {"playlist": "5235806268525753666", "token": IPTVEDITOR_TOKEN}
        
        try:
            response = requests.post(url, headers=HTTP_HEADERS, json=payload)
            response.raise_for_status()
            return response.json()['items']
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get categories: {str(e)}")
            raise

    def get_shows(self) -> List[Dict]:
        """Get shows from IPTV Editor API"""
        url = f"{IPTVEDITOR_BASE_URL}/stream/series/get-data"
        payload = {"playlist": "5235806268525753666", "token": IPTVEDITOR_TOKEN}
        
        try:
            response = requests.post(url, headers=HTTP_HEADERS, json=payload)
            response.raise_for_status()
            return response.json()['items']
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get shows: {str(e)}")
            raise

    def get_episodes(self, series_id: int) -> Dict:
        """Get episodes from IPTV Editor"""
        url = f"{IPTVEDITOR_BASE_URL}/episode/get-data"
        payload = {
            "seriesId": str(series_id),
            "url": None,
            "token": IPTVEDITOR_TOKEN
        }
        
        try:
            response = requests.post(url, headers=HTTP_HEADERS, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get episodes: {str(e)}")
            raise

    def update_show(self, show_id: int, show_tmdb_id: int, show_category: int) -> Dict:
        """Update show information in IPTV Editor"""
        url = f"{IPTVEDITOR_BASE_URL}/stream/series/save"
        payload = {
            "items": [{
                "id": show_id,
                "tmdb": show_tmdb_id,
                "youtube_trailer": "",
                "category": show_category
            }],
            "checkSaved": False,
            "token": IPTVEDITOR_TOKEN
        }
        
        try:
            response = requests.post(url, headers=HTTP_HEADERS, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to update show: {str(e)}")
            raise

import logging
import requests
from typing import Dict, List, Optional

from config import (
    TMDB_API_KEY, IPTVEDITOR_TOKEN, HTTP_HEADERS,
    IPTVEDITOR_BASE_URL, TMDB_BASE_URL, FALLBACK_TO_FIRST_RESULT
)
from utils import detect_language
from database import cache_manager

# Special response for shows not found in TMDB
NOT_FOUND_RESPONSE = {
    "not_found": True,
    "reason": "No results found in TMDB"
}

class TMDBApi:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def search_show(self, query: str) -> Optional[Dict]:
        """Search for show on TMDB with cache support"""
        self.logger.info(f"Searching for show: {query}")
        
        # Check cache first
        cached_result = cache_manager.get_tmdb_search(query)
        if cached_result:
            self.logger.info(f"Found cached search result for '{query}'")
            # If it's a "not found" result, log and return None
            if cached_result.get('not_found'):
                self.logger.info(f"Show '{query}' was previously marked as not found in TMDB")
                return None
            return cached_result
        
        self.logger.info(f"No cache found, searching TMDB API for: {query}")
        
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
                # Cache the "not found" result
                cache_manager.cache_tmdb_search(query, NOT_FOUND_RESPONSE)
                return None
            
            # Try to find exact title match first
            exact_matches = [
                result for result in data['results']
                if result.get('name', '').lower() == query.lower() or 
                   result.get('original_name', '').lower() == query.lower()
            ]
            
            if exact_matches:
                self.logger.info(f"Found exact title match for '{query}'")
                result = exact_matches[0]
                cache_manager.cache_tmdb_search(query, result)
                return result
            
            # Then try language match
            lang_matches = [
                result for result in data['results']
                if result.get('original_language') == detected_lang
            ]
            
            if lang_matches:
                self.logger.info(f"Found match in detected language ({detected_lang})")
                result = lang_matches[0]
                cache_manager.cache_tmdb_search(query, result)
                return result
            
            # Fall back to first result if allowed
            if FALLBACK_TO_FIRST_RESULT:
                self.logger.warning(
                    f"No matches found for '{query}' in language '{detected_lang}', "
                    "using first available result as fallback"
                )
                result = data['results'][0]
                cache_manager.cache_tmdb_search(query, result)
                return result
            
            self.logger.error(
                f"No suitable matches found for '{query}' "
                f"(language: {detected_lang}, fallback disabled)"
            )
            # Cache the "not found" result
            cache_manager.cache_tmdb_search(query, NOT_FOUND_RESPONSE)
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"TMDB API request failed: {str(e)}")
            raise
        except (KeyError, IndexError) as e:
            self.logger.error(f"Failed to parse TMDB response: {str(e)}")
            raise

    def get_show_details(self, show_id: int) -> Optional[Dict]:
        """Get detailed show information from TMDB with cache support"""
        self.logger.info(f"Getting details for TMDB ID: {show_id}")
        
        # Check cache first
        cached_result = cache_manager.get_tmdb_details(show_id)
        if cached_result:
            self.logger.info(f"Found cached details for TMDB ID {show_id}")
            return cached_result
        
        self.logger.info(f"No cache found, fetching details from TMDB API for ID: {show_id}")
        
        url = f"{TMDB_BASE_URL}/tv/{show_id}"
        params = {
            'language': 'en-us',
            'api_key': TMDB_API_KEY,
            'append_to_response': 'images,credits,videos'
        }
        
        try:
            response = requests.get(url, headers=HTTP_HEADERS, params=params)
            response.raise_for_status()
            result = response.json()
            
            # Cache the result
            cache_manager.cache_tmdb_details(show_id, result)
            self.logger.info(f"Cached details for TMDB ID {show_id}")
            
            return result
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

    def get_episodes(self, show_id: int) -> Optional[Dict]:
        """Get episodes from IPTV Editor with cache support"""
        self.logger.info(f"Getting episodes for show ID: {show_id}")
        
        # Check cache first
        cached_result = cache_manager.get_iptveditor_episodes(show_id)
        if cached_result:
            self.logger.info(f"Found cached episodes for show ID {show_id}")
            return cached_result
        
        self.logger.info(f"No cache found, fetching episodes from API for show ID: {show_id}")
        
        url = f"{IPTVEDITOR_BASE_URL}/episode/get-data"
        payload = {
            "seriesId": str(show_id),
            "url": None,
            "token": IPTVEDITOR_TOKEN
        }
        
        try:
            response = requests.post(url, headers=HTTP_HEADERS, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Cache the result
            cache_manager.cache_iptveditor_episodes(show_id, result)
            self.logger.info(f"Cached episodes for show ID {show_id}")
            
            return result
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get episodes: {str(e)}")
            raise

    def update_show(self, show_id: int, show_tmdb_id: int, show_category: int) -> Dict:
        """Update show information in IPTV Editor with cache support"""
        self.logger.info(f"Updating show ID {show_id} with TMDB ID {show_tmdb_id}")
        
        # Check cache first
        cached_result = cache_manager.get_iptveditor_update(show_id, show_tmdb_id, show_category)
        if cached_result:
            self.logger.info(f"Found cached update result for show ID {show_id}")
            return cached_result
        
        self.logger.info(f"No cache found, updating show via API: {show_id}")
        
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
            result = response.json()
            
            # Cache the result
            cache_manager.cache_iptveditor_update(show_id, show_tmdb_id, show_category, result)
            self.logger.info(f"Cached update result for show ID {show_id}")
            
            return result
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to update show: {str(e)}")
            raise

import logging
from typing import Dict, List

from config import STATE_FILE, CATEGORIES_FILE, SHOWS_FILE
from utils import load_json_file, save_json_file
from api import TMDBApi, IPTVEditorApi
from database import cache_manager

class IPTVEditor:
    def __init__(self, use_api: bool = True, batch_size: int = 10):
        self.logger = logging.getLogger(__name__)
        self.use_api = use_api
        self.batch_size = batch_size
        
        # Initialize API clients
        self.tmdb_api = TMDBApi()
        self.iptv_api = IPTVEditorApi()
        
        # Initialize data
        self.categories = []
        self.shows = []
        
        # Load initial data
        self.load_data()
        self.load_state()

    def load_state(self) -> None:
        """Load the processing state from file"""
        try:
            state = load_json_file(STATE_FILE)
            self.state = state
            self.logger.debug(f"Loaded state: {state}")
        except FileNotFoundError:
            self.state = {'last_processed_index': 0}
            self.logger.debug("Starting new processing session")

    def save_state(self) -> None:
        """Save the current processing state to file"""
        save_json_file(STATE_FILE, self.state)
        self.logger.debug(f"Saved state: {self.state}")

    def load_data(self) -> None:
        """Load categories and shows data"""
        try:
            source = "API" if self.use_api else "local files"
            self.logger.debug(f"Loading data from {source}")
            
            if self.use_api:
                self.categories = self.iptv_api.get_categories()
                self.shows = self.iptv_api.get_shows()
            else:
                self.categories = load_json_file(CATEGORIES_FILE)['items']
                self.shows = load_json_file(SHOWS_FILE)['items']
            
            self.logger.debug(f"Loaded {len(self.categories)} categories and {len(self.shows)} shows")
        except Exception as e:
            self.logger.error(f"Failed to load data: {str(e)}")
            raise

    def process_show(self, show: Dict) -> None:
        """Process a single show"""
        show_id = show['id']
        show_name = show['name']
        
        self.logger.debug(f"Processing show: {show_name} (ID: {show_id})")
        
        try:
            # Get show info from TMDB
            show_info = self.tmdb_api.search_show(show_name)
            if not show_info:
                self.logger.debug(f"Could not find show '{show_name}' on TMDB")
                self.logger.info("✗")
                return
            
            show_tmdb_id = show_info['id']
            self.logger.debug(f"TMDB match - ID: {show_tmdb_id}, Name: {show_info.get('name')}")
            
            # Get detailed show information
            show_details = self.tmdb_api.get_show_details(show_tmdb_id)
            self.logger.debug(f"Retrieved show details from TMDB")
            
            # Get show episodes
            episodes = self.iptv_api.get_episodes(show_id)
            self.logger.debug(f"Retrieved {len(episodes) if episodes else 0} episodes")
            
            # Update the show
            result = self.iptv_api.update_show(show_id, show_tmdb_id, show['category'])
            self.logger.info("✓")
            
        except Exception as e:
            self.logger.debug(f"Error processing show '{show_name}': {str(e)}")
            self.logger.info("✗")

    def process_shows(self) -> None:
        """Process shows in batches, starting from the last processed index"""
        start_idx = self.state['last_processed_index']
        end_idx = min(start_idx + self.batch_size, len(self.shows))
        total_shows = len(self.shows)
        
        self.logger.info(f"Processing shows {start_idx + 1}-{end_idx} of {total_shows}")
        
        try:
            for i in range(start_idx, end_idx):
                show = self.shows[i]
                self.logger.info(f"[{i + 1}/{total_shows}] {show['name']} ", extra={'terminator': ''})
                
                try:
                    self.process_show(show)
                except Exception as e:
                    self.logger.debug(f"Failed to process show: {str(e)}")
                finally:
                    # Update state regardless of success/failure
                    self.state['last_processed_index'] = i + 1
                    self.save_state()
        finally:
            # Report cache statistics
            cache_manager.report_stats()
            
            # Print processing summary using root logger to access all handlers
            root_logger = logging.getLogger()
            for handler in root_logger.handlers:
                if isinstance(handler, logging.Handler) and hasattr(handler, 'get_summary'):
                    summary = handler.get_summary()
                    if summary:
                        # Use root logger to ensure message goes through all handlers
                        root_logger.info(summary)

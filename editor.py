import logging
from typing import Dict, List

from config import STATE_FILE, CATEGORIES_FILE, SHOWS_FILE
from utils import load_json_file, save_json_file
from api import TMDBApi, IPTVEditorApi

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
            self.logger.info(f"Resuming from show index {self.state['last_processed_index']}")
        except FileNotFoundError:
            self.state = {'last_processed_index': 0}
            self.logger.info("Starting new processing session")

    def save_state(self) -> None:
        """Save the current processing state to file"""
        save_json_file(STATE_FILE, self.state)
        self.logger.debug(f"Saved state: last_processed_index = {self.state['last_processed_index']}")

    def load_data(self) -> None:
        """Load categories and shows data"""
        try:
            if self.use_api:
                self.logger.info("Loading data from API...")
                self.categories = self.iptv_api.get_categories()
                self.shows = self.iptv_api.get_shows()
            else:
                self.logger.info("Loading data from local JSON files...")
                self.categories = load_json_file(CATEGORIES_FILE)['items']
                self.shows = load_json_file(SHOWS_FILE)['items']
            
            self.logger.info(f"Loaded {len(self.categories)} categories and {len(self.shows)} shows")
        except Exception as e:
            self.logger.error(f"Failed to load data: {str(e)}")
            raise

    def process_show(self, show: Dict) -> None:
        """Process a single show"""
        self.logger.info(f"Processing show: {show['name']}")
        
        try:
            # Get show info from TMDB
            show_info = self.tmdb_api.search_show(show['name'])
            if not show_info:
                self.logger.error(f"Could not find show '{show['name']}' on TMDB")
                return
            
            show_tmdb_id = show_info['id']
            self.logger.info(f"Found TMDB match: {show_info.get('name')} (ID: {show_tmdb_id})")
            
            # Update the show
            result = self.iptv_api.update_show(show['id'], show_tmdb_id, show['category'])
            self.logger.info(f"Successfully updated show: {show['name']}")
            
        except Exception as e:
            self.logger.error(f"Error processing show '{show['name']}': {str(e)}")
            raise

    def process_shows(self) -> None:
        """Process shows in batches, starting from the last processed index"""
        start_idx = self.state['last_processed_index']
        end_idx = min(start_idx + self.batch_size, len(self.shows))
        
        self.logger.info(f"Processing shows {start_idx + 1} to {end_idx} of {len(self.shows)}")
        
        for i in range(start_idx, end_idx):
            show = self.shows[i]
            self.logger.info(f"\nProcessing show {i + 1}/{len(self.shows)}: {show['name']}")
            
            try:
                self.process_show(show)
            except Exception as e:
                self.logger.error(f"Failed to process show: {str(e)}")
            finally:
                # Update state regardless of success/failure
                self.state['last_processed_index'] = i + 1
                self.save_state()

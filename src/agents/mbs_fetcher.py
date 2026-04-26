"""MBS Data Fetcher Agent."""
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class MBSDataFetcher:
    """Autonomous agent for fetching MBS item data."""
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or Path(__file__).parent.parent / "data" / "mbs_items.json"
        self._cache: Dict[str, Any] = {}
        self._last_updated: Optional[datetime] = None
        logger.info(f"MBSDataFetcher initialized with data path: {self.data_path}")
    
    def fetch_mbs_item(self, item_number: str) -> Optional[Dict[str, Any]]:
        """Fetch a single MBS item by its item number."""
        if not self._validate_item_number(item_number):
            logger.error(f"Invalid MBS item number: {item_number}")
            raise ValueError(f"Invalid MBS item number: '{item_number}'. Must be 4-5 digits.")
        
        if item_number in self._cache:
            logger.info(f"Cache hit for MBS item {item_number}")
            return self._cache[item_number]
        
        item = self._load_from_source(item_number)
        
        if item:
            self._cache[item_number] = item
            logger.info(f"Successfully fetched MBS item {item_number}")
        else:
            logger.warning(f"MBS item {item_number} not found in data source")
        
        return item
    
    def fetch_multiple_items(self, item_numbers: list[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Fetch multiple MBS items at once."""
        results = {}
        for item_number in item_numbers:
            try:
                results[item_number] = self.fetch_mbs_item(item_number)
            except ValueError as e:
                logger.error(f"Error fetching item {item_number}: {e}")
                results[item_number] = None
        return results
    
    def get_all_items(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all available MBS items."""
        data = self._load_all_data()
        self._cache.update(data)
        return data
    
    def _validate_item_number(self, item_number: str) -> bool:
        """Validate MBS item number format."""
        if not isinstance(item_number, str):
            return False
        return item_number.isdigit() and 4 <= len(item_number) <= 5
    
    def _load_from_source(self, item_number: str) -> Optional[Dict[str, Any]]:
        """Load MBS item from data source."""
        try:
            all_data = self._load_all_data()
            return all_data.get(item_number)
        except Exception as e:
            logger.error(f"Error loading MBS data: {e}")
            return None
    
    def _load_all_data(self) -> Dict[str, Dict[str, Any]]:
        """Load all MBS data from the configured source."""
        if self.data_path in self._cache:
            return self._cache.get(self.data_path, {})
        
        path = Path(self.data_path)
        if not path.exists():
            logger.error(f"MBS data file not found: {path}")
            raise FileNotFoundError(f"MBS data file not found: {path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self._last_updated = datetime.now()
            self._cache[self.data_path] = data
            logger.info(f"Loaded {len(data)} MBS items from {path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in MBS data file: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading MBS data: {e}")
            raise
    
    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()
        self._last_updated = None
        logger.info("MBS Data Fetcher cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state."""
        return {
            "cached_items": len([k for k in self._cache.keys() if k != self.data_path]),
            "last_updated": self._last_updated.isoformat() if self._last_updated else None,
            "data_source": str(self.data_path),
        }


def fetch_mbs_item(item_number: str, data_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Convenience function to fetch a single MBS item."""
    fetcher = MBSDataFetcher(data_path)
    return fetcher.fetch_mbs_item(item_number)

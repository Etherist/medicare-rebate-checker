#!/usr/bin/env python3
"""Initialize MBS data cache for improved startup performance."""
import sys
import os

# Add project src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.mbs_fetcher import MBSDataFetcher


def main():
    """Load all MBS items into cache."""
    print("Initializing MBS data cache...")
    fetcher = MBSDataFetcher()
    all_items = fetcher.get_all_items()
    print(f"✓ Cache initialized with {len(all_items)} MBS items")
    print(f"✓ Cache info: {fetcher.get_cache_info()}")


if __name__ == '__main__':
    main()
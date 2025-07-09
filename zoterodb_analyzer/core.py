"""Core functionality for ZoteroAnalyzer."""

import os
from typing import List, Optional, Dict, Any, Union
from pyzotero import zotero
import logging
from .models import ZoteroItem, FilterCriteria, ItemType, LiteratureCategory

logger = logging.getLogger(__name__)


class ZoteroAnalyzer:
    """Main class for analyzing Zotero databases and fetching literature data."""

    def __init__(self, library_id: str, library_type: str = 'user', api_key: Optional[str] = None, local: bool = False):
        """
        Initialize ZoteroAnalyzer.

        Args:
            library_id: Zotero library ID (user ID or group ID)
            library_type: 'user' or 'group'
            api_key: Zotero API key. If not provided, will look for ZOTERO_API_KEY env var
        """
        self.library_id = library_id
        self.library_type = library_type

        if api_key is None:
            api_key = os.getenv('ZOTERO_API_KEY')
            if api_key is None:
                raise ValueError("API key must be provided or set as ZOTERO_API_KEY environment variable")

        self.api_key = api_key
        if local:
            # FIXME: seems not working
            self.zot = zotero.Zotero(library_id="", library_type="user", api_key="", local=True)
        else:
            self.zot = zotero.Zotero(library_id, library_type, api_key)

        # Cache for collections and tags
        self._collections_cache = None
        self._tags_cache = None

    def get_collections(self, refresh: bool = False) -> Dict[str, str]:
        """
        Get all collections from the library.

        Args:
            refresh: Force refresh of cached collections

        Returns:
            Dict mapping collection names to collection keys
        """
        if self._collections_cache is None or refresh:
            try:
                collections = self.zot.collections()
                self._collections_cache = {
                    coll['data']['name']: coll['key']
                    for coll in collections
                }
            except Exception as e:
                logger.error(f"Error fetching collections: {e}")
                self._collections_cache = {}

        return self._collections_cache

    def get_tags(self, refresh: bool = False) -> List[str]:
        """
        Get all tags from the library.

        Args:
            refresh: Force refresh of cached tags

        Returns:
            List of tag names
        """
        if self._tags_cache is None or refresh:
            try:
                tags = self.zot.tags()
                self._tags_cache = [tag['tag'] for tag in tags]
            except Exception as e:
                logger.error(f"Error fetching tags: {e}")
                self._tags_cache = []

        return self._tags_cache

    def fetch_items(self,
                    filter_criteria: Optional[FilterCriteria] = None,
                    limit: Optional[int] = None) -> List[ZoteroItem]:
        """
        Fetch items from Zotero library with optional filtering.

        Args:
            filter_criteria: Criteria for filtering items
            limit: Maximum number of items to fetch (None for all items)

        Returns:
            List of ZoteroItem objects
        """
        try:
            # Fetch items with pagination
            if filter_criteria and filter_criteria.collections:
                # If collections are specified, fetch from those collections
                items = []
                collections = self.get_collections()
                for collection_name in filter_criteria.collections:
                    collection_key = collections.get(collection_name)
                    if collection_key:
                        collection_items = self._fetch_items_paginated(
                            fetch_func=lambda **params: self.zot.collection_items_top(collection_key, **params),
                            limit=limit
                        )
                        items.extend(collection_items)
            else:
                # Fetch all items with pagination
                items = self._fetch_items_paginated(
                    fetch_func=lambda **params: self.zot.top(**params),
                    limit=limit
                )

            # Convert to ZoteroItem objects
            zotero_items = []
            for item in items:
                try:
                    zotero_item = ZoteroItem.from_zotero_item(item)

                    # Add collection information
                    if 'collections' in item.get('data', {}):
                        collection_keys = item['data']['collections']
                        collections_map = self.get_collections()
                        collection_names = [
                            name for name, key in collections_map.items()
                            if key in collection_keys
                        ]
                        zotero_item.collections = collection_names

                    zotero_items.append(zotero_item)
                except Exception as e:
                    logger.warning(f"Error processing item {item.get('key', 'unknown')}: {e}")
                    continue

            # Apply additional filtering
            if filter_criteria:
                zotero_items = self._apply_filters(zotero_items, filter_criteria)

            return zotero_items

        except Exception as e:
            logger.error(f"Error fetching items: {e}")
            raise

    def _fetch_items_paginated(self, fetch_func, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch items with pagination to get more than 100 items.

        Args:
            fetch_func: Function to call for fetching items (e.g., self.zot.top)
            limit: Maximum number of items to fetch (None for all items)

        Returns:
            List of raw item dictionaries from Zotero API
        """
        all_items = []
        start = 0
        batch_size = 100  # Zotero API limit per request

        logger.info(f"Starting to fetch items with pagination (limit: {limit})")

        while True:
            # Calculate how many items to fetch in this batch
            if limit is not None:
                remaining = limit - len(all_items)
                if remaining <= 0:
                    break
                current_batch_size = min(batch_size, remaining)
            else:
                current_batch_size = batch_size

            # Fetch current batch
            params = {
                'start': start,
                'limit': current_batch_size
            }

            try:
                batch_items = fetch_func(**params)

                if not batch_items:
                    # No more items available
                    logger.info(f"No more items found. Total fetched: {len(all_items)}")
                    break

                all_items.extend(batch_items)
                start += len(batch_items)

                logger.info(f"Fetched batch: {len(batch_items)} items (total: {len(all_items)})")

                # If we got fewer items than requested, we've reached the end
                if len(batch_items) < current_batch_size:
                    logger.info(f"Reached end of library. Total items fetched: {len(all_items)}")
                    break

            except Exception as e:
                logger.error(f"Error fetching batch starting at {start}: {e}")
                break

        logger.info(f"Pagination complete. Total items fetched: {len(all_items)}")
        return all_items

    def _apply_filters(self, items: List[ZoteroItem], criteria: FilterCriteria) -> List[ZoteroItem]:
        """Apply filtering criteria to items."""
        filtered_items = items

        # Filter by tags
        if criteria.tags:
            filtered_items = [
                item for item in filtered_items
                if any(tag in item.tags for tag in criteria.tags)
            ]

        # Filter by item types
        if criteria.item_types:
            item_type_values = [t.value for t in criteria.item_types]
            filtered_items = [
                item for item in filtered_items
                if item.item_type in item_type_values
            ]

        # Filter by authors
        if criteria.authors:
            filtered_items = [
                item for item in filtered_items
                if any(
                    any(author_filter.lower() in author.lower()
                        for author in item.authors)
                    for author_filter in criteria.authors
                )
            ]

        # Filter by date range
        if criteria.date_range:
            start_year, end_year = criteria.date_range
            filtered_items = [
                item for item in filtered_items
                if item.year and start_year <= item.year <= end_year
            ]

        # Filter by title content
        if criteria.title_contains:
            filtered_items = [
                item for item in filtered_items
                if criteria.title_contains.lower() in item.title.lower()
            ]

        # Filter by keywords (searches in title and abstract)
        if criteria.keywords:
            filtered_items = [
                item for item in filtered_items
                if any(
                    keyword.lower() in (item.title + ' ' + (item.abstract or '')).lower()
                    for keyword in criteria.keywords
                )
            ]

        return filtered_items

    def categorize_items(self,
                         items: List[ZoteroItem],
                         categories: List[LiteratureCategory]) -> Dict[str, LiteratureCategory]:
        """
        Categorize items based on predefined categories and their keywords.

        Args:
            items: List of ZoteroItem objects to categorize
            categories: List of LiteratureCategory objects with keywords

        Returns:
            Dict mapping category names to updated LiteratureCategory objects
        """
        # Initialize categories dict
        categorized = {cat.name: LiteratureCategory(
            name=cat.name,
            description=cat.description,
            keywords=cat.keywords
        ) for cat in categories}

        # Add an "Uncategorized" category for items that don't match any category
        categorized["Uncategorized"] = LiteratureCategory(
            name="Uncategorized",
            description="Items that don't match any specified category"
        )

        for item in items:
            item_text = (item.title + ' ' + (item.abstract or '') + ' ' + ' '.join(item.tags)).lower()
            categorized_flag = False

            for category in categories:
                # Check if any keywords match
                if any(keyword.lower() in item_text for keyword in category.keywords):
                    categorized[category.name].add_item(item)
                    categorized_flag = True
                    break  # Item goes to first matching category

            if not categorized_flag:
                categorized["Uncategorized"].add_item(item)

        return categorized

    def get_bibtex(self, item_keys: List[str]) -> Dict[str, str]:
        """
        Get BibTeX citations for specified items.

        Args:
            item_keys: List of Zotero item keys

        Returns:
            Dict mapping item keys to BibTeX strings
        """
        try:
            bibtex_dict = {}
            for key in item_keys:
                try:
                    bibtex = self.zot.item(key, format='bibtex')
                    bibtex_dict[key] = bibtex
                except Exception as e:
                    logger.warning(f"Error fetching BibTeX for item {key}: {e}")
                    bibtex_dict[key] = ""

            return bibtex_dict
        except Exception as e:
            logger.error(f"Error fetching BibTeX: {e}")
            return {}

    def search_items(self, query: str, limit: Optional[int] = None) -> List[ZoteroItem]:
        """
        Search items using Zotero's search functionality.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching ZoteroItem objects
        """
        try:
            params = {'q': query}
            if limit:
                params['limit'] = limit

            items = self.zot.items(**params)

            zotero_items = []
            for item in items:
                try:
                    zotero_item = ZoteroItem.from_zotero_item(item)
                    zotero_items.append(zotero_item)
                except Exception as e:
                    logger.warning(f"Error processing search result {item.get('key', 'unknown')}: {e}")
                    continue

            return zotero_items

        except Exception as e:
            logger.error(f"Error searching items: {e}")
            return []

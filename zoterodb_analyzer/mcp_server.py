"""Model Context Protocol (MCP) interface for ZoteroDB Analyzer."""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .core import ZoteroAnalyzer
from .exporter import ContentExporter
from .models import FilterCriteria, LiteratureCategory, ExportFormat, ItemType

logger = logging.getLogger(__name__)


class ZoteroMCPServer:
    """MCP server for ZoteroDB Analyzer that provides tools for LLM agents."""

    def __init__(self, default_library_id: Optional[str] = None,
                 default_library_type: str = 'user',
                 default_api_key: Optional[str] = None):
        """
        Initialize MCP server.

        Args:
            default_library_id: Default Zotero library ID
            default_library_type: Default library type ('user' or 'group')
            default_api_key: Default Zotero API key
        """
        self.default_library_id = default_library_id
        self.default_library_type = default_library_type
        self.default_api_key = default_api_key
        self.analyzers = {}  # Cache analyzers by library_id
        self.exporter = ContentExporter("mcp_output")

    def get_analyzer(self, library_id: Optional[str] = None,
                     library_type: Optional[str] = None,
                     api_key: Optional[str] = None) -> ZoteroAnalyzer:
        """Get or create a ZoteroAnalyzer instance."""
        lib_id = library_id or self.default_library_id
        lib_type = library_type or self.default_library_type
        key = api_key or self.default_api_key

        if not lib_id:
            raise ValueError("Library ID must be provided")

        cache_key = f"{lib_id}_{lib_type}"
        if cache_key not in self.analyzers:
            self.analyzers[cache_key] = ZoteroAnalyzer(lib_id, lib_type, key)

        return self.analyzers[cache_key]

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools."""
        return [
            {
                "name": "fetch_literature",
                "description": "Fetch literature items from Zotero library with filtering options",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "library_id": {"type": "string", "description": "Zotero library ID"},
                        "library_type": {"type": "string", "enum": ["user", "group"], "default": "user"},
                        "api_key": {"type": "string", "description": "Zotero API key"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                        "collections": {"type": "array", "items": {"type": "string"}, "description": "Filter by collections"},
                        "authors": {"type": "array", "items": {"type": "string"}, "description": "Filter by authors"},
                        "keywords": {"type": "array", "items": {"type": "string"}, "description": "Filter by keywords"},
                        "year_range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "description": "Year range [start, end]"},
                        "item_type": {"type": "string", "enum": [t.value for t in ItemType], "description": "Filter by item type"},
                        "limit": {"type": "integer", "description": "Maximum number of items to fetch"}
                    }
                }
            },
            {
                "name": "categorize_literature",
                "description": "Categorize literature items based on predefined categories",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "library_id": {"type": "string", "description": "Zotero library ID"},
                        "library_type": {"type": "string", "enum": ["user", "group"], "default": "user"},
                        "api_key": {"type": "string", "description": "Zotero API key"},
                        "categories": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "keywords": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["name", "keywords"]
                            },
                            "description": "Literature categories with keywords for classification"
                        },
                        "filter_criteria": {
                            "type": "object",
                            "properties": {
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "collections": {"type": "array", "items": {"type": "string"}},
                                "authors": {"type": "array", "items": {"type": "string"}},
                                "keywords": {"type": "array", "items": {"type": "string"}},
                                "year_range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
                                "item_type": {"type": "string", "enum": [t.value for t in ItemType]}
                            },
                            "description": "Optional filter criteria for items"
                        },
                        "export_format": {"type": "string", "enum": ["json", "markdown", "both"], "default": "markdown"},
                        "context_type": {"type": "string", "enum": ["related_works", "literature_review"], "default": "related_works"}
                    },
                    "required": ["categories"]
                }
            },
            {
                "name": "search_literature",
                "description": "Search literature items in Zotero library",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "library_id": {"type": "string", "description": "Zotero library ID"},
                        "library_type": {"type": "string", "enum": ["user", "group"], "default": "user"},
                        "api_key": {"type": "string", "description": "Zotero API key"},
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 20}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_collections",
                "description": "Get all collections from Zotero library",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "library_id": {"type": "string", "description": "Zotero library ID"},
                        "library_type": {"type": "string", "enum": ["user", "group"], "default": "user"},
                        "api_key": {"type": "string", "description": "Zotero API key"}
                    }
                }
            },
            {
                "name": "get_tags",
                "description": "Get all tags from Zotero library",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "library_id": {"type": "string", "description": "Zotero library ID"},
                        "library_type": {"type": "string", "enum": ["user", "group"], "default": "user"},
                        "api_key": {"type": "string", "description": "Zotero API key"},
                        "limit": {"type": "integer", "description": "Maximum number of tags to return", "default": 100}
                    }
                }
            },
            {
                "name": "export_for_llm",
                "description": "Export literature data in LLM-optimized format for context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "categorized_data": {
                            "type": "object",
                            "description": "Categorized literature data from categorize_literature"
                        },
                        "context_type": {"type": "string", "enum": ["related_works", "literature_review"], "default": "related_works"},
                        "format": {"type": "string", "enum": ["markdown", "json"], "default": "markdown"}
                    },
                    "required": ["categorized_data"]
                }
            }
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool call."""
        try:
            if name == "fetch_literature":
                return await self._fetch_literature(arguments)
            elif name == "categorize_literature":
                return await self._categorize_literature(arguments)
            elif name == "search_literature":
                return await self._search_literature(arguments)
            elif name == "get_collections":
                return await self._get_collections(arguments)
            elif name == "get_tags":
                return await self._get_tags(arguments)
            elif name == "export_for_llm":
                return await self._export_for_llm(arguments)
            else:
                return {"error": f"Unknown tool: {name}"}

        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {"error": str(e)}

    async def _fetch_literature(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch literature items."""
        analyzer = self.get_analyzer(
            args.get('library_id'),
            args.get('library_type'),
            args.get('api_key')
        )

        # Build filter criteria
        filter_criteria = FilterCriteria()
        if 'tags' in args:
            filter_criteria.tags = args['tags']
        if 'collections' in args:
            filter_criteria.collections = args['collections']
        if 'authors' in args:
            filter_criteria.authors = args['authors']
        if 'keywords' in args:
            filter_criteria.keywords = args['keywords']
        if 'year_range' in args:
            filter_criteria.date_range = tuple(args['year_range'])
        if 'item_type' in args:
            filter_criteria.item_types = [ItemType(args['item_type'])]

        items = analyzer.fetch_items(filter_criteria, args.get('limit'))

        return {
            "success": True,
            "count": len(items),
            "items": [item.to_dict() for item in items],
            "timestamp": datetime.now().isoformat()
        }

    async def _categorize_literature(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize literature items."""
        analyzer = self.get_analyzer(
            args.get('library_id'),
            args.get('library_type'),
            args.get('api_key')
        )

        # Build categories
        categories = []
        for cat_data in args['categories']:
            categories.append(LiteratureCategory(
                name=cat_data['name'],
                description=cat_data.get('description'),
                keywords=cat_data['keywords']
            ))

        # Build filter criteria if provided
        filter_criteria = None
        if 'filter_criteria' in args:
            fc_args = args['filter_criteria']
            filter_criteria = FilterCriteria()
            if 'tags' in fc_args:
                filter_criteria.tags = fc_args['tags']
            if 'collections' in fc_args:
                filter_criteria.collections = fc_args['collections']
            if 'authors' in fc_args:
                filter_criteria.authors = fc_args['authors']
            if 'keywords' in fc_args:
                filter_criteria.keywords = fc_args['keywords']
            if 'year_range' in fc_args:
                filter_criteria.date_range = tuple(fc_args['year_range'])
            if 'item_type' in fc_args:
                filter_criteria.item_types = [ItemType(fc_args['item_type'])]

        # Fetch and categorize items
        items = analyzer.fetch_items(filter_criteria)
        categorized_items = analyzer.categorize_items(items, categories)

        # Export files
        export_format = ExportFormat(args.get('export_format', 'markdown'))
        exported_files = self.exporter.export_categorized_items(
            categorized_items, export_format
        )

        # Create LLM context
        context_type = args.get('context_type', 'related_works')
        llm_context_file = self.exporter.export_for_llm_context(
            categorized_items, context_type
        )

        return {
            "success": True,
            "categories": {name: cat.to_dict() for name, cat in categorized_items.items()},
            "total_items": sum(len(cat.items) for cat in categorized_items.values()),
            "exported_files": exported_files,
            "llm_context_file": llm_context_file,
            "timestamp": datetime.now().isoformat()
        }

    async def _search_literature(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search literature items."""
        analyzer = self.get_analyzer(
            args.get('library_id'),
            args.get('library_type'),
            args.get('api_key')
        )

        items = analyzer.search_items(args['query'], args.get('limit', 20))

        return {
            "success": True,
            "query": args['query'],
            "count": len(items),
            "items": [item.to_dict() for item in items],
            "timestamp": datetime.now().isoformat()
        }

    async def _get_collections(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get collections from library."""
        analyzer = self.get_analyzer(
            args.get('library_id'),
            args.get('library_type'),
            args.get('api_key')
        )

        collections = analyzer.get_collections()

        return {
            "success": True,
            "collections": collections,
            "count": len(collections),
            "timestamp": datetime.now().isoformat()
        }

    async def _get_tags(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get tags from library."""
        analyzer = self.get_analyzer(
            args.get('library_id'),
            args.get('library_type'),
            args.get('api_key')
        )

        tags = analyzer.get_tags()
        limit = args.get('limit', 100)

        return {
            "success": True,
            "tags": tags[:limit],
            "total_count": len(tags),
            "returned_count": min(len(tags), limit),
            "timestamp": datetime.now().isoformat()
        }

    async def _export_for_llm(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Export data for LLM consumption."""
        categorized_data = args['categorized_data']
        context_type = args.get('context_type', 'related_works')
        format_type = args.get('format', 'markdown')

        # Reconstruct categorized items from data
        categorized_items = {}
        for name, cat_data in categorized_data.items():
            category = LiteratureCategory(
                name=cat_data['name'],
                description=cat_data.get('description'),
                keywords=cat_data.get('keywords', [])
            )

            # Add items to category
            for item_data in cat_data.get('items', []):
                # Create ZoteroItem from dict
                item = ZoteroItem(
                    key=item_data['key'],
                    title=item_data['title'],
                    authors=item_data.get('authors', []),
                    abstract=item_data.get('abstract'),
                    year=item_data.get('year'),
                    journal=item_data.get('journal'),
                    doi=item_data.get('doi'),
                    tags=item_data.get('tags', []),
                    item_type=item_data.get('item_type')
                )
                category.add_item(item)

            categorized_items[name] = category

        if format_type == 'markdown':
            output_file = self.exporter.export_for_llm_context(categorized_items, context_type)

            # Read the content to return
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "format": "markdown",
                "content": content,
                "file_path": output_file,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # JSON format
            export_data = {
                "context_type": context_type,
                "generated_at": datetime.now().isoformat(),
                "categories": {name: cat.to_dict() for name, cat in categorized_items.items()}
            }

            return {
                "success": True,
                "format": "json",
                "content": export_data,
                "timestamp": datetime.now().isoformat()
            }

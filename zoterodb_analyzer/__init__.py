"""
ZoteroDB Analyzer - A Python package for Zotero database analysis and literature review composition.

This package provides tools to:
1. Fetch content from Zotero user accounts with filtering capabilities
2. Export filtered content in JSON and Markdown formats for LLM agents
3. Provide MCP interface for agent-based literature review composition
"""

__version__ = "0.1.0"
__author__ = "ZoteroDB Analyzer Team"
__email__ = "contact@zoterodb-analyzer.com"

from .core import ZoteroAnalyzer
from .exporter import ContentExporter
from .models import ZoteroItem, FilterCriteria, ExportFormat

__all__ = [
    "ZoteroAnalyzer",
    "ContentExporter", 
    "ZoteroItem",
    "FilterCriteria",
    "ExportFormat",
]
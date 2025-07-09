"""Configuration and utilities for ZoteroDB Analyzer."""

import os
import logging
from pathlib import Path
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_config_dir() -> Path:
    """Get the configuration directory for ZoteroDB Analyzer."""
    config_dir = Path.home() / '.zoterodb_analyzer'
    config_dir.mkdir(exist_ok=True)
    return config_dir


def load_env_config() -> dict:
    """Load configuration from environment variables."""
    return {
        'library_id': os.getenv('ZOTERO_LIBRARY_ID'),
        'library_type': os.getenv('ZOTERO_LIBRARY_TYPE', 'user'),
        'api_key': os.getenv('ZOTERO_API_KEY'),
        'output_dir': os.getenv('ZOTERODB_OUTPUT_DIR', 'output'),
        'log_level': os.getenv('ZOTERODB_LOG_LEVEL', 'INFO'),
    }


class ZoteroConfig:
    """Configuration manager for ZoteroDB Analyzer."""

    def __init__(self):
        self.config = load_env_config()
        setup_logging(self.config['log_level'])

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value."""
        return self.config.get(key, default)

    def validate_credentials(self) -> bool:
        """Validate that required credentials are available."""
        return bool(self.config['library_id'] and self.config['api_key'])

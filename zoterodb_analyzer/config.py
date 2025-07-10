"""Configuration and utilities for ZoteroDB Analyzer."""

import os
import logging
from pathlib import Path
from typing import Optional


def load_dotenv(dotenv_path: Optional[Path] = None) -> None:
    """Load environment variables from .env file."""
    if dotenv_path is None:
        # Look for .env file in current directory and parent directories
        current_dir = Path.cwd()
        for path in [current_dir] + list(current_dir.parents):
            env_file = path / ".env"
            if env_file.exists():
                dotenv_path = env_file
                break

    if dotenv_path and dotenv_path.exists():
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if value:  # Only set non-empty values
                        os.environ[key] = value


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_config_dir() -> Path:
    """Get the configuration directory for ZoteroDB Analyzer."""
    config_dir = Path.home() / ".zoterodb_analyzer"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def load_env_config() -> dict:
    """Load configuration from environment variables and .env file."""
    # Load .env file first
    load_dotenv()

    return {
        "library_id": os.getenv("ZOTERO_LIBRARY_ID"),
        "library_type": os.getenv("ZOTERO_LIBRARY_TYPE", "user"),
        "api_key": os.getenv("ZOTERO_API_KEY"),
        "output_dir": os.getenv("DEFAULT_OUTPUT_DIR", "output"),
        "log_level": os.getenv("ZOTERODB_LOG_LEVEL", "INFO"),
        "default_limit": os.getenv("DEFAULT_LIMIT"),
    }


class ZoteroConfig:
    """Configuration manager for ZoteroDB Analyzer."""

    def __init__(self):
        self.config = load_env_config()
        setup_logging(self.config["log_level"])

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value."""
        return self.config.get(key, default)

    def validate_credentials(self) -> bool:
        """Validate that required credentials are available."""
        return bool(self.config["library_id"] and self.config["api_key"])

    def get_credentials(self) -> tuple[Optional[str], str, Optional[str]]:
        """Get Zotero credentials (library_id, library_type, api_key)."""
        return (
            self.config["library_id"],
            self.config["library_type"],
            self.config["api_key"],
        )

    def print_setup_instructions(self) -> None:
        """Print instructions for setting up credentials."""
        print("🔧 ZoteroDB Analyzer Setup")
        print("=" * 40)
        print("\n1. Get your Zotero credentials:")
        print("   • API Key: https://www.zotero.org/settings/keys")
        print("   • User ID: Check your profile URL")
        print("\n2. Create a .env file in your project directory:")
        print("   cp .env.example .env")
        print("\n3. Edit .env file with your credentials:")
        print("   ZOTERO_LIBRARY_ID=your_user_id")
        print("   ZOTERO_API_KEY=your_api_key")
        print("   ZOTERO_LIBRARY_TYPE=user")
        print("\n4. Run the program again!")


# Global config instance
config = ZoteroConfig()

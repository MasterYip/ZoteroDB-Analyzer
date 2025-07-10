#!/usr/bin/env python3
"""
Example usage of ZoteroDB Analyzer for literature review composition.

This example demonstrates the complete workflow:
1. Connecting to Zotero library
2. Fetching and filtering literature
3. Categorizing papers by research themes
4. Exporting for LLM consumption
"""

import os
import json
import platform
from pathlib import Path

from zoterodb_analyzer import (
    ZoteroAnalyzer,
    ContentExporter,
    FilterCriteria,
    LiteratureCategory,
    ExportFormat,
    ItemType,
)
from zoterodb_analyzer.config import config


def print_credential_instructions():
    """Print OS-specific instructions for setting environment variables."""
    system = platform.system().lower()

    print("⚠️  Please set your Zotero credentials:")
    print("\nGet your credentials from: https://www.zotero.org/settings/keys")
    print("1. Go to Zotero Settings > API Keys")
    print("2. Create a new private key with library access")
    print("3. Note your User ID and API Key")

    if system == "windows":
        print("\n📋 For Windows Command Prompt:")
        print("   set ZOTERO_LIBRARY_ID=your_user_id")
        print("   set ZOTERO_API_KEY=your_api_key")

        print("\n📋 For Windows PowerShell:")
        print("   $env:ZOTERO_LIBRARY_ID='your_user_id'")
        print("   $env:ZOTERO_API_KEY='your_api_key'")

        print("\n📋 For permanent Windows environment variables:")
        print("   1. Press Win+R, type 'sysdm.cpl', press Enter")
        print("   2. Go to Advanced > Environment Variables")
        print("   3. Add ZOTERO_LIBRARY_ID and ZOTERO_API_KEY")

    else:  # Linux/macOS
        print("\n📋 For Linux/macOS:")
        print("   export ZOTERO_LIBRARY_ID='your_user_id'")
        print("   export ZOTERO_API_KEY='your_api_key'")

        print("\n📋 To make it permanent, add to ~/.bashrc or ~/.zshrc:")
        print(
            "   echo 'export ZOTERO_LIBRARY_ID=\"your_user_id\"' >> ~/.bashrc"
        )
        print("   echo 'export ZOTERO_API_KEY=\"your_api_key\"' >> ~/.bashrc")

    print("\n💡 Alternative: You can also pass credentials directly in code:")
    print(
        "   analyzer = ZoteroAnalyzer('your_user_id', 'user', 'your_api_key')"
    )


def main():
    """Main example workflow."""

    # Configuration - try to get from .env file first, then environment variables
    LIBRARY_ID = config.get("library_id") or os.getenv(
        "ZOTERO_LIBRARY_ID", "your_user_id_here"
    )
    API_KEY = config.get("api_key") or os.getenv(
        "ZOTERO_API_KEY", "your_api_key_here"
    )
    LIBRARY_TYPE = config.get("library_type") or "user"

    if (
        LIBRARY_ID == "your_user_id_here"
        or API_KEY == "your_api_key_here"
        or not LIBRARY_ID
        or not API_KEY
    ):
        print("❌ Missing Zotero credentials!")
        config.print_setup_instructions()
        return

    print("🔄 Initializing ZoteroDB Analyzer...")

    try:
        # Initialize analyzer
        analyzer = ZoteroAnalyzer(
            library_id=LIBRARY_ID, library_type=LIBRARY_TYPE, api_key=API_KEY
        )

        print("✅ Connected to Zotero library")

        # Example 1: Basic fetching with filters
        print("\n📚 Example 1: Fetching recent papers...")
        filter_criteria = FilterCriteria(
            date_range=(
                2000,
                2024,
            ),  # Fixed: changed from year_range to date_range
            item_types=[
                ItemType.JOURNAL_ARTICLE,
                ItemType.CONFERENCE_PAPER,
                ItemType.PREPRINT,
            ],
            keywords=[],
        )

        items = analyzer.fetch_items(filter_criteria, limit=None)
        print(f"Found {len(items)} items matching criteria")

        if items:
            print(f"Sample item: {items[0].title}")
            print(f"Authors: {', '.join(items[0].authors)}")
            print(f"Year: {items[0].year}")

        # Example 2: Literature categorization
        print("\n🏷️  Example 2: Categorizing literature...")

        # Load categories from JSON file
        categories_file = Path("examples/categories.json")
        if categories_file.exists():
            with open(categories_file, "r", encoding="utf-8") as f:
                categories_data = json.load(f)

            categories = [
                LiteratureCategory(
                    name=cat["name"],
                    description=cat["description"],
                    keywords=cat["keywords"],
                )
                for cat in categories_data
            ]

            # Categorize items
            categorized_items = analyzer.categorize_items(items, categories)

            print("📊 Categorization results:")
            for name, category in categorized_items.items():
                print(f"   {name}: {len(category.items)} items")

        # Example 3: Export for LLM consumption
        print("\n📤 Example 3: Exporting for LLM agents...")

        exporter = ContentExporter("output")

        # Export individual items
        exported_files = exporter.export_items(
            items,
            format=ExportFormat.BOTH,
            filename_prefix="example_literature",
        )

        print("Exported files:")
        for format_name, filepath in exported_files.items():
            print(f"   {format_name}: {filepath}")

        # Export categorized items if we have categories
        if "categorized_items" in locals():
            exporter.export_categorized_items(
                categorized_items,
                format=ExportFormat.MARKDOWN,
                filename_prefix="categorized_example",
            )

            # Create LLM context file
            llm_context = exporter.export_for_llm_context(
                categorized_items, context_type="related_works"
            )

            print(f"\nLLM Context file: {llm_context}")
            print(
                "📋 This file is optimized for LLM agents to compose literature reviews!"
            )

        # Example 4: Search functionality
        print("\n🔍 Example 4: Searching literature...")
        search_results = analyzer.search_items("deep learning", limit=5)

        print(f"Found {len(search_results)} items for 'deep learning':")
        for item in search_results[:3]:  # Show first 3
            print(f"   • {item.title} ({item.year})")

        print("\n✅ Example completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Check the 'output' directory for exported files")
        print("   2. Use the LLM context file with Claude or GPT-4")
        print("   3. Try the CLI: zoterodb-analyzer --help")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("   1. Check your Zotero API credentials")
        print("   2. Ensure your library has some items")
        print("   3. Check your internet connection")
        print("   4. Verify your User ID is correct (should be numeric)")


if __name__ == "__main__":
    main()

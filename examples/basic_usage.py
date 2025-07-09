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
from pathlib import Path

from zoterodb_analyzer import (
    ZoteroAnalyzer, 
    ContentExporter, 
    FilterCriteria, 
    LiteratureCategory,
    ExportFormat,
    ItemType
)


def main():
    """Main example workflow."""
    
    # Configuration - replace with your actual credentials
    LIBRARY_ID = os.getenv('ZOTERO_LIBRARY_ID', 'your_user_id_here')
    API_KEY = os.getenv('ZOTERO_API_KEY', 'your_api_key_here')
    
    if LIBRARY_ID == 'your_user_id_here' or API_KEY == 'your_api_key_here':
        print("⚠️  Please set your Zotero credentials:")
        print("   export ZOTERO_LIBRARY_ID='your_user_id'")
        print("   export ZOTERO_API_KEY='your_api_key'")
        print("\nGet credentials from: https://www.zotero.org/settings/keys")
        return
    
    print("🔄 Initializing ZoteroDB Analyzer...")
    
    try:
        # Initialize analyzer
        analyzer = ZoteroAnalyzer(
            library_id=LIBRARY_ID,
            library_type='user',
            api_key=API_KEY
        )
        
        print("✅ Connected to Zotero library")
        
        # Example 1: Basic fetching with filters
        print("\n📚 Example 1: Fetching recent papers...")
        filter_criteria = FilterCriteria(
            year_range=(2020, 2024),
            item_types=[ItemType.JOURNAL_ARTICLE],
            keywords=["machine learning", "robotics", "AI"]
        )
        
        items = analyzer.fetch_items(filter_criteria, limit=20)
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
            with open(categories_file, 'r', encoding='utf-8') as f:
                categories_data = json.load(f)
            
            categories = [
                LiteratureCategory(
                    name=cat['name'],
                    description=cat['description'],
                    keywords=cat['keywords']
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
            filename_prefix="example_literature"
        )
        
        print("Exported files:")
        for format_name, filepath in exported_files.items():
            print(f"   {format_name}: {filepath}")
        
        # Export categorized items if we have categories
        if 'categorized_items' in locals():
            categorized_files = exporter.export_categorized_items(
                categorized_items,
                format=ExportFormat.MARKDOWN,
                filename_prefix="categorized_example"
            )
            
            # Create LLM context file
            llm_context = exporter.export_for_llm_context(
                categorized_items,
                context_type="related_works"
            )
            
            print(f"\nLLM Context file: {llm_context}")
            print("📋 This file is optimized for LLM agents to compose literature reviews!")
        
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


if __name__ == "__main__":
    main()
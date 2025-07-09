"""Command-line interface for ZoteroDB Analyzer."""

import click
import os
import json
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import ZoteroAnalyzer
from .exporter import ContentExporter
from .models import FilterCriteria, LiteratureCategory, ExportFormat, ItemType


console = Console()


@click.group()
@click.version_option()
def main():
    """ZoteroDB Analyzer - Analyze Zotero databases for literature review composition."""
    pass


@main.command()
@click.option('--library-id', required=True, help='Zotero library ID')
@click.option('--library-type', default='user', type=click.Choice(['user', 'group']), help='Library type')
@click.option('--api-key', help='Zotero API key (or set ZOTERO_API_KEY env var)')
@click.option('--tags', help='Filter by tags (comma-separated)')
@click.option('--collections', help='Filter by collections (comma-separated)')
@click.option('--authors', help='Filter by authors (comma-separated)')
@click.option('--keywords', help='Filter by keywords in title/abstract (comma-separated)')
@click.option('--year-range', help='Filter by year range (e.g., 2020-2023)')
@click.option('--item-type', help='Filter by item type', 
              type=click.Choice([t.value for t in ItemType]))
@click.option('--limit', type=int, help='Maximum number of items to fetch')
@click.option('--output-dir', default='output', help='Output directory')
@click.option('--format', default='both', 
              type=click.Choice(['json', 'markdown', 'both']), help='Export format')
@click.option('--categories-file', help='JSON file with literature categories')
@click.option('--include-bibtex/--no-bibtex', default=True, help='Include BibTeX citations')
def fetch(library_id, library_type, api_key, tags, collections, authors, keywords, 
          year_range, item_type, limit, output_dir, format, categories_file, include_bibtex):
    """Fetch and export literature from Zotero library."""
    
    try:
        # Initialize analyzer
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task("Initializing Zotero connection...", total=None)
            analyzer = ZoteroAnalyzer(library_id, library_type, api_key)
        
        # Build filter criteria
        filter_criteria = FilterCriteria()
        
        if tags:
            filter_criteria.tags = [tag.strip() for tag in tags.split(',')]
        if collections:
            filter_criteria.collections = [col.strip() for col in collections.split(',')]
        if authors:
            filter_criteria.authors = [author.strip() for author in authors.split(',')]
        if keywords:
            filter_criteria.keywords = [kw.strip() for kw in keywords.split(',')]
        if year_range:
            start_year, end_year = map(int, year_range.split('-'))
            filter_criteria.date_range = (start_year, end_year)
        if item_type:
            filter_criteria.item_types = [ItemType(item_type)]
        
        # Fetch items
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task("Fetching items from Zotero...", total=None)
            items = analyzer.fetch_items(filter_criteria, limit)
        
        console.print(f"[green]Fetched {len(items)} items[/green]")
        
        # Initialize exporter
        exporter = ContentExporter(output_dir)
        
        # Handle categorization if categories file provided
        if categories_file and os.path.exists(categories_file):
            with open(categories_file, 'r', encoding='utf-8') as f:
                categories_data = json.load(f)
            
            categories = [
                LiteratureCategory(
                    name=cat['name'],
                    description=cat.get('description'),
                    keywords=cat.get('keywords', [])
                )
                for cat in categories_data
            ]
            
            categorized_items = analyzer.categorize_items(items, categories)
            
            # Export categorized items
            export_format = ExportFormat(format)
            exported_files = exporter.export_categorized_items(
                categorized_items, export_format, include_bibtex=include_bibtex
            )
            
            # Also create LLM context file
            context_file = exporter.export_for_llm_context(categorized_items)
            exported_files['llm_context'] = context_file
            
            # Display category summary
            table = Table(title="Literature Categories")
            table.add_column("Category", style="cyan")
            table.add_column("Items", justify="right", style="magenta")
            table.add_column("Description", style="green")
            
            for name, category in categorized_items.items():
                table.add_row(
                    name, 
                    str(len(category.items)), 
                    category.description or "No description"
                )
            
            console.print(table)
        else:
            # Export regular items
            export_format = ExportFormat(format)
            exported_files = exporter.export_items(
                items, export_format, include_bibtex=include_bibtex
            )
        
        # Display exported files
        console.print("\n[bold green]Exported files:[/bold green]")
        for format_name, filepath in exported_files.items():
            console.print(f"  {format_name}: [blue]{filepath}[/blue]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@main.command()
@click.option('--library-id', required=True, help='Zotero library ID')
@click.option('--library-type', default='user', type=click.Choice(['user', 'group']), help='Library type')
@click.option('--api-key', help='Zotero API key (or set ZOTERO_API_KEY env var)')
def collections(library_id, library_type, api_key):
    """List all collections in the Zotero library."""
    
    try:
        analyzer = ZoteroAnalyzer(library_id, library_type, api_key)
        collections = analyzer.get_collections()
        
        if collections:
            table = Table(title="Zotero Collections")
            table.add_column("Collection Name", style="cyan")
            table.add_column("Collection Key", style="magenta")
            
            for name, key in collections.items():
                table.add_row(name, key)
            
            console.print(table)
        else:
            console.print("[yellow]No collections found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@main.command()
@click.option('--library-id', required=True, help='Zotero library ID')
@click.option('--library-type', default='user', type=click.Choice(['user', 'group']), help='Library type')
@click.option('--api-key', help='Zotero API key (or set ZOTERO_API_KEY env var)')
@click.option('--limit', type=int, default=50, help='Maximum number of tags to show')
def tags(library_id, library_type, api_key, limit):
    """List tags in the Zotero library."""
    
    try:
        analyzer = ZoteroAnalyzer(library_id, library_type, api_key)
        tags = analyzer.get_tags()
        
        if tags:
            # Sort and limit tags
            sorted_tags = sorted(tags)[:limit]
            
            console.print(f"[green]Found {len(tags)} tags (showing first {len(sorted_tags)}):[/green]")
            for tag in sorted_tags:
                console.print(f"  • {tag}")
        else:
            console.print("[yellow]No tags found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@main.command()
@click.option('--library-id', required=True, help='Zotero library ID')
@click.option('--library-type', default='user', type=click.Choice(['user', 'group']), help='Library type')
@click.option('--api-key', help='Zotero API key (or set ZOTERO_API_KEY env var)')
@click.option('--query', required=True, help='Search query')
@click.option('--limit', type=int, default=20, help='Maximum number of results')
@click.option('--output-dir', default='output', help='Output directory')
@click.option('--format', default='both', 
              type=click.Choice(['json', 'markdown', 'both']), help='Export format')
def search(library_id, library_type, api_key, query, limit, output_dir, format):
    """Search items in Zotero library."""
    
    try:
        analyzer = ZoteroAnalyzer(library_id, library_type, api_key)
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task(f"Searching for '{query}'...", total=None)
            items = analyzer.search_items(query, limit)
        
        if items:
            console.print(f"[green]Found {len(items)} items matching '{query}'[/green]")
            
            # Display results table
            table = Table(title="Search Results")
            table.add_column("Title", style="cyan", max_width=50)
            table.add_column("Authors", style="green", max_width=30)
            table.add_column("Year", justify="right", style="magenta")
            table.add_column("Journal", style="yellow", max_width=30)
            
            for item in items[:10]:  # Show first 10 in table
                authors_str = ", ".join(item.authors[:2])
                if len(item.authors) > 2:
                    authors_str += " et al."
                
                table.add_row(
                    item.title[:50] + "..." if len(item.title) > 50 else item.title,
                    authors_str,
                    str(item.year) if item.year else "N/A",
                    (item.journal[:30] + "...") if item.journal and len(item.journal) > 30 else (item.journal or "N/A")
                )
            
            console.print(table)
            
            # Export results
            exporter = ContentExporter(output_dir)
            export_format = ExportFormat(format)
            exported_files = exporter.export_items(items, export_format, f"search_{query.replace(' ', '_')}")
            
            console.print("\n[bold green]Exported files:[/bold green]")
            for format_name, filepath in exported_files.items():
                console.print(f"  {format_name}: [blue]{filepath}[/blue]")
        else:
            console.print(f"[yellow]No items found matching '{query}'[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@main.command()
@click.argument('categories_file', type=click.Path(exists=True))
def validate_categories(categories_file):
    """Validate a categories JSON file."""
    
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        
        if not isinstance(categories_data, list):
            console.print("[red]Error: Categories file must contain a JSON array[/red]")
            return
        
        console.print(f"[green]Categories file is valid with {len(categories_data)} categories:[/green]")
        
        table = Table(title="Categories")
        table.add_column("Name", style="cyan")
        table.add_column("Keywords", style="green")
        table.add_column("Description", style="yellow")
        
        for cat in categories_data:
            name = cat.get('name', 'N/A')
            keywords = ', '.join(cat.get('keywords', []))
            description = cat.get('description', 'No description')
            
            table.add_row(name, keywords, description)
        
        console.print(table)
        
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON Error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    main()
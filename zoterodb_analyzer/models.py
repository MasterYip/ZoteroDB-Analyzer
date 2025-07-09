"""Data models for ZoteroDB Analyzer."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import json


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    MARKDOWN = "markdown"
    BOTH = "both"


class ItemType(Enum):
    """Zotero item types."""
    # Academic Publications
    JOURNAL_ARTICLE = "journalArticle"
    CONFERENCE_PAPER = "conferencePaper"
    PREPRINT = "preprint"

    # Books and Chapters
    BOOK = "book"
    BOOK_SECTION = "bookSection"

    # Academic Works
    THESIS = "thesis"
    DISSERTATION = "thesis"  # Alias for thesis

    # Reports and Documents
    REPORT = "report"
    WORKING_PAPER = "report"  # Often categorized as report
    WHITE_PAPER = "report"   # Often categorized as report

    # Web and Digital
    WEBPAGE = "webpage"
    BLOG_POST = "blogPost"
    FORUM_POST = "forumPost"

    # Legal and IP
    PATENT = "patent"
    CASE = "case"
    STATUTE = "statute"
    BILL = "bill"

    # Media and Arts
    ARTWORK = "artwork"
    AUDIO_RECORDING = "audioRecording"
    VIDEO_RECORDING = "videoRecording"
    FILM = "film"
    TV_BROADCAST = "tvBroadcast"
    RADIO_BROADCAST = "radioBroadcast"
    PODCAST = "podcast"

    # News and Magazines
    NEWSPAPER_ARTICLE = "newspaperArticle"
    MAGAZINE_ARTICLE = "magazineArticle"

    # Reference Works
    ENCYCLOPEDIA_ARTICLE = "encyclopediaArticle"
    DICTIONARY_ENTRY = "dictionaryEntry"

    # Software and Data
    COMPUTER_PROGRAM = "computerProgram"
    SOFTWARE = "computerProgram"  # Alias
    DATASET = "computerProgram"   # Often categorized as computer program

    # Presentations and Events
    PRESENTATION = "presentation"
    CONFERENCE_PRESENTATION = "presentation"  # Alias

    # Correspondence
    EMAIL = "email"
    LETTER = "letter"
    INSTANT_MESSAGE = "instantMessage"

    # Interviews and Personal
    INTERVIEW = "interview"
    PERSONAL_COMMUNICATION = "interview"  # Often categorized as interview

    # Documents and Archives
    DOCUMENT = "document"
    MANUSCRIPT = "manuscript"
    MAP = "map"

    # Academic Infrastructure
    HEARING = "hearing"


@dataclass
class FilterCriteria:
    """Criteria for filtering Zotero items."""
    tags: Optional[List[str]] = None
    collections: Optional[List[str]] = None
    item_types: Optional[List[ItemType]] = None
    authors: Optional[List[str]] = None
    date_range: Optional[tuple] = None  # (start_year, end_year)
    keywords: Optional[List[str]] = None
    title_contains: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tags": self.tags,
            "collections": self.collections,
            "item_types": [t.value for t in self.item_types] if self.item_types else None,
            "authors": self.authors,
            "date_range": self.date_range,
            "keywords": self.keywords,
            "title_contains": self.title_contains,
        }


@dataclass
class ZoteroItem:
    """Represents a Zotero library item with relevant metadata."""
    key: str
    title: str
    authors: List[str] = field(default_factory=list)
    abstract: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    collections: List[str] = field(default_factory=list)
    item_type: Optional[str] = None
    bibtex: Optional[str] = None
    date_added: Optional[str] = None
    date_modified: Optional[str] = None
    extra: Optional[str] = None

    def __post_init__(self):
        """Ensure authors is always a list."""
        if self.authors is None:
            self.authors = []
        if isinstance(self.authors, str):
            self.authors = [self.authors]

    @classmethod
    def from_zotero_item(cls, item: Dict[str, Any]) -> 'ZoteroItem':
        """Create ZoteroItem from Zotero API response."""
        data = item.get('data', {})

        # Extract authors
        creators = data.get('creators', [])
        authors = []
        for creator in creators:
            if creator.get('creatorType') in ['author', 'editor']:
                if 'name' in creator:
                    authors.append(creator['name'])
                else:
                    first_name = creator.get('firstName', '')
                    last_name = creator.get('lastName', '')
                    full_name = f"{first_name} {last_name}".strip()
                    if full_name:
                        authors.append(full_name)

        # Extract tags
        tags = [tag.get('tag', '') for tag in data.get('tags', [])]

        # Extract year from date
        date_str = data.get('date', '')
        year = None
        if date_str:
            try:
                # Try to extract year from various date formats
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
                if year_match:
                    year = int(year_match.group())
            except:
                pass

        return cls(
            key=item.get('key', ''),
            title=data.get('title', ''),
            authors=authors,
            abstract=data.get('abstractNote', ''),
            year=year,
            journal=data.get('publicationTitle', ''),
            volume=data.get('volume', ''),
            issue=data.get('issue', ''),
            pages=data.get('pages', ''),
            doi=data.get('DOI', ''),
            url=data.get('url', ''),
            tags=tags,
            collections=[],  # Will be populated separately
            item_type=data.get('itemType', ''),
            date_added=data.get('dateAdded', ''),
            date_modified=data.get('dateModified', ''),
            extra=data.get('extra', ''),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "year": self.year,
            "journal": self.journal,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "doi": self.doi,
            "url": self.url,
            "tags": self.tags,
            "collections": self.collections,
            "item_type": self.item_type,
            "bibtex": self.bibtex,
            "date_added": self.date_added,
            "date_modified": self.date_modified,
            "extra": self.extra,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def get_citation(self) -> str:
        """Generate a basic citation string."""
        authors_str = ", ".join(self.authors[:3])  # Limit to first 3 authors
        if len(self.authors) > 3:
            authors_str += " et al."

        citation_parts = []
        if authors_str:
            citation_parts.append(authors_str)
        if self.year:
            citation_parts.append(f"({self.year})")
        if self.title:
            citation_parts.append(f'"{self.title}"')
        if self.journal:
            citation_parts.append(self.journal)

        return ". ".join(citation_parts)


@dataclass
class LiteratureCategory:
    """Represents a category for organizing literature."""
    name: str
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    items: List[ZoteroItem] = field(default_factory=list)

    def add_item(self, item: ZoteroItem):
        """Add an item to this category."""
        if item not in self.items:
            self.items.append(item)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "items": [item.to_dict() for item in self.items],
            "item_count": len(self.items),
        }

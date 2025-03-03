#!/usr/bin/env python3
"""
stufflog - A general journalling CLI application that uses YAML files.

This application allows you to create and manage "stufflogs" for different categories
like books, movies, moods, etc. It stores entries with timestamps, titles, ratings,
and optional comments in human-readable YAML files.
"""

import argparse
import datetime
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any


class StufflogError(Exception):
    """Base exception for stufflog-specific errors."""
    pass


def get_stufflog_dir() -> Path:
    """
    Get the directory where stufflog files are stored.
    
    Returns:
        Path: The directory path where stufflog files should be stored.
    """
    stufflog_dir = os.environ.get('STUFFLOG_DIR')
    if stufflog_dir:
        directory = Path(stufflog_dir)
    else:
        directory = Path.home() / '.stufflog'
    
    # Create the directory if it doesn't exist
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    
    return directory


def get_stufflog_path(category: str) -> Path:
    """
    Get the path to a specific stufflog file.
    
    Args:
        category: The category name for the stufflog.
        
    Returns:
        Path: The file path for the specified stufflog category.
    """
    return get_stufflog_dir() / f"{category}.yml"


def load_stufflog(category: str) -> Dict:
    """
    Load a stufflog file for a given category.
    
    Args:
        category: The category name for the stufflog.
        
    Returns:
        Dict: The loaded stufflog data.
        
    Raises:
        StufflogError: If the stufflog file doesn't exist.
    """
    file_path = get_stufflog_path(category)
    
    if not file_path.exists():
        raise StufflogError(f"No stufflog found for category '{category}'. "
                           f"Use 'stufflog {category} init' to create one.")
    
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file) or {}
            # Ensure the 'Entries' key exists
            if 'Entries' not in data:
                data['Entries'] = {}
            return data
        except yaml.YAMLError as e:
            raise StufflogError(f"Error parsing YAML file: {e}")


def save_stufflog(category: str, data: Dict) -> None:
    """
    Save data to a stufflog file.
    
    Args:
        category: The category name for the stufflog.
        data: The data to save.
    """
    file_path = get_stufflog_path(category)
    
    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False)


def init_stufflog(category: str) -> None:
    """
    Initialize a new stufflog for the given category.
    
    Args:
        category: The category name for the new stufflog.
        
    Raises:
        StufflogError: If a stufflog with the given category already exists.
    """
    file_path = get_stufflog_path(category)
    
    if file_path.exists():
        raise StufflogError(f"A stufflog with the category '{category}' already exists.")
    
    # Create an empty stufflog with the basic structure
    data = {
        'Entries': {}
    }
    
    save_stufflog(category, data)
    print(f"Initialized stufflog for category '{category}'")


def add_entry(category: str, title: str, rating: int, comment: Optional[str] = None) -> None:
    """
    Add a new entry to a stufflog.
    
    Args:
        category: The category name for the stufflog.
        title: The title of the entry.
        rating: The rating (numeric) for the entry.
        comment: An optional comment for the entry.
        
    Raises:
        StufflogError: If an entry with the same title already exists.
    """
    data = load_stufflog(category)
    
    if title in data['Entries']:
        raise StufflogError(
            f"An entry titled '{title}' already exists. "
            f"Did you mean 'stufflog {category} edit {title} --rating={rating}'?"
        )
    
    # Create a new entry
    entry = {
        'Datetime': datetime.datetime.now().isoformat(),
        'Title': title,
        'Rating': rating
    }
    
    if comment:
        entry['Comment'] = comment
    
    # Add the entry to the stufflog
    data['Entries'][title] = entry
    
    save_stufflog(category, data)
    print(f"Added entry '{title}' to {category} stufflog")


def delete_entry(category: str, title: str) -> None:
    """
    Delete an entry from a stufflog.
    
    Args:
        category: The category name for the stufflog.
        title: The title of the entry to delete.
        
    Raises:
        StufflogError: If no entry with the given title exists.
    """
    data = load_stufflog(category)
    
    if title not in data['Entries']:
        raise StufflogError(f"No entry titled '{title}' found in {category} stufflog.")
    
    # Delete the entry
    del data['Entries'][title]
    
    save_stufflog(category, data)
    print(f"Deleted entry '{title}' from {category} stufflog")


def query_entries(
    category: str,
    greater_than: Optional[int] = None,
    less_than: Optional[int] = None,
    after: Optional[str] = None,
    before: Optional[str] = None
) -> List[Dict]:
    """
    Query entries in a stufflog based on various filters.
    
    Args:
        category: The category name for the stufflog.
        greater_than: Filter for entries with rating greater than this value.
        less_than: Filter for entries with rating less than this value.
        after: Filter for entries with datetime after this value.
        before: Filter for entries with datetime before this value.
        
    Returns:
        List[Dict]: A list of entries that match the query criteria.
    """
    data = load_stufflog(category)
    results = []
    
    for title, entry in data['Entries'].items():
        # Check if the entry meets all the filter criteria
        include = True
        
        if greater_than is not None and entry.get('Rating', 0) <= greater_than:
            include = False
            
        if less_than is not None and entry.get('Rating', 0) >= less_than:
            include = False
            
        if after is not None:
            entry_date = datetime.datetime.fromisoformat(entry.get('Datetime', ''))
            filter_date = datetime.datetime.fromisoformat(after)
            if entry_date <= filter_date:
                include = False
                
        if before is not None:
            entry_date = datetime.datetime.fromisoformat(entry.get('Datetime', ''))
            filter_date = datetime.datetime.fromisoformat(before)
            if entry_date >= filter_date:
                include = False
        
        if include:
            entry_copy = entry.copy()
            entry_copy['Title'] = title
            results.append(entry_copy)
    
    return results


def search_entries(category: str, search_term: str) -> List[Dict]:
    """
    Search for entries in a stufflog that contain a given text in title or comment.
    
    Args:
        category: The category name for the stufflog.
        search_term: The text to search for in entry titles and comments.
        
    Returns:
        List[Dict]: A list of entries that match the search criteria.
    """
    data = load_stufflog(category)
    results = []
    search_term = search_term.lower()  # Convert to lowercase for case-insensitive search
    
    for title, entry in data['Entries'].items():
        # Check if the search term is in the title or comment
        title_match = search_term in title.lower()
        comment_match = 'Comment' in entry and search_term in entry['Comment'].lower()
        
        if title_match or comment_match:
            entry_copy = entry.copy()
            entry_copy['Title'] = title
            results.append(entry_copy)
    
    return results


def display_entries(entries: List[Dict]) -> None:
    """
    Display a list of entries in a readable format.
    
    Args:
        entries: The list of entries to display.
    """
    if not entries:
        print("No matching entries found.")
        return
    
    print(f"Found {len(entries)} matching entries:")
    print()
    
    for entry in entries:
        print(f"## {entry.get('Title', 'Untitled')}")
        print(f"- **Datetime**: {entry.get('Datetime', 'Unknown')}")
        print(f"- **Rating**: {entry.get('Rating', 'No rating')}")
        
        if 'Comment' in entry:
            print(f"- **Comment**: {entry['Comment']}")
            
        print()


def main():
    """Main entry point for the stufflog CLI application."""
    parser = argparse.ArgumentParser(
        description="A general journalling CLI application that uses YAML files."
    )
    
    parser.add_argument(
        "category",
        help="Category for the stufflog (e.g., books, movies)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new stufflog")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new entry to a stufflog")
    add_parser.add_argument("title", help="Title of the entry")
    add_parser.add_argument("rating", type=int, help="Rating for the entry")
    add_parser.add_argument("comment", nargs="?", help="Optional comment for the entry")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query entries in a stufflog")
    query_parser.add_argument("--greater-than", type=int, help="Filter by rating greater than")
    query_parser.add_argument("--less-than", type=int, help="Filter by rating less than")
    query_parser.add_argument("--after", help="Filter by datetime after (ISO format)")
    query_parser.add_argument("--before", help="Filter by datetime before (ISO format)")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an entry from a stufflog")
    delete_parser.add_argument("title", help="Title of the entry to delete")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for text in entry titles and comments")
    search_parser.add_argument("term", help="Text to search for")
    
    args = parser.parse_args()
    
    try:
        if args.command == "init":
            init_stufflog(args.category)
        
        elif args.command == "add":
            add_entry(args.category, args.title, args.rating, args.comment)
        
        elif args.command == "query":
            entries = query_entries(
                args.category,
                args.greater_than,
                args.less_than,
                args.after,
                args.before
            )
            display_entries(entries)
        
        elif args.command == "delete":
            delete_entry(args.category, args.title)
        
        elif args.command == "search":
            entries = search_entries(args.category, args.term)
            display_entries(entries)
        
        else:
            parser.print_help()
            
    except StufflogError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


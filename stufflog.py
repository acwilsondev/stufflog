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
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from git_service import GitService


class StufflogError(Exception):
    """Base exception for stufflog-specific errors."""
    pass


class StufflogApp:
    """
    A class that encapsulates the functionality of the stufflog application.
    """
    
    def __init__(self, git_service: Optional[GitService] = None):
        """
        Initialize the StufflogApp with optional GitService dependency.
        
        Args:
            git_service: The GitService to use for git operations. If None,
                         a new GitService will be created.
        """
        self.git_service = git_service or GitService()
    
    def get_stufflog_dir(self) -> Path:
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


    def get_stufflog_path(self, category: str) -> Path:
        """
        Get the path to a specific stufflog file.
        
        Args:
            category: The category name for the stufflog.
            
        Returns:
            Path: The file path for the specified stufflog category.
        """
        return self.get_stufflog_dir() / f"{category}.yml"


    def load_stufflog(self, category: str) -> Dict:
        """
        Load a stufflog file for a given category.
        
        Args:
            category: The category name for the stufflog.
            
        Returns:
            Dict: The loaded stufflog data.
            
        Raises:
            StufflogError: If the stufflog file doesn't exist.
        """
        # If git remotes are configured, try to pull changes first
        # If git remotes are configured, try to pull changes first
        if self.git_service.has_remotes():
            self.git_service.pull()
        file_path = self.get_stufflog_path(category)
        
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

    def save_stufflog(self, category: str, data: Dict) -> None:
        """
        Save data to a stufflog file.
        
        Args:
            category: The category name for the stufflog.
            data: The data to save.
        """
        file_path = self.get_stufflog_path(category)
        
        with open(file_path, 'w') as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)
        
        # Attempt to push changes if git is set up with remotes
        # Attempt to push changes if git is set up with remotes
        if self.git_service.has_remotes():
            self.git_service.push()
    def delete_entry(self, category: str, title: str) -> None:
        """
        Delete an entry from a stufflog.
        
        Args:
            category: The category name for the stufflog.
            title: The title of the entry to delete.
            
        Raises:
            StufflogError: If no entry with the given title exists.
        """
        data = self.load_stufflog(category)
        
        if title not in data['Entries']:
            raise StufflogError(f"No entry titled '{title}' found in {category} stufflog.")
        
        # Delete the entry
        del data['Entries'][title]
        
        self.save_stufflog(category, data)
        print(f"Deleted entry '{title}' from {category} stufflog")


    def query_entries(
        self,
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
        data = self.load_stufflog(category)
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


    def search_entries(self, category: str, search_term: str) -> List[Dict]:
        """
        Search for entries in a stufflog that contain a given text in title or comment.
        
        Args:
            category: The category name for the stufflog.
            search_term: The text to search for in entry titles and comments.
            
        Returns:
            List[Dict]: A list of entries that match the search criteria.
        """
        data = self.load_stufflog(category)
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


    def display_entries(self, entries: List[Dict]) -> None:
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


    def open_stufflog_dir(self):
        """
        Open a new shell in the stufflog directory.
        """
        stufflog_dir = self.get_stufflog_dir()
        print(f"Opening shell in {stufflog_dir}")
        
        # Determine the user's shell
        user_shell = os.environ.get('SHELL', '/bin/sh')
        
        # Open a new shell in the stufflog directory
        try:
            subprocess.run([user_shell], cwd=stufflog_dir)
        except Exception as e:
            raise StufflogError(f"Failed to open shell: {e}")

    def setup_git_remote(self, remote_url: str, remote_name: str = "origin") -> bool:
        """
        Set up a remote repository for the git repository.
        
        Args:
            remote_url: URL of the remote repository
            remote_name: Name for the remote (default: origin)
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.git_service.setup_remote(remote_url, remote_name)
            
    def init_stufflog(self, category: str) -> None:
        """
        Initialize a new stufflog file.
        
        Args:
            category: The category name for the new stufflog.
        """
        file_path = self.get_stufflog_path(category)
        
        if file_path.exists():
            raise StufflogError(f"Stufflog for category '{category}' already exists.")
        
        # Initialize with empty data structure
        data = {
            "Entries": {}
        }
        
        self.save_stufflog(category, data)
        print(f"Initialized new stufflog for category '{category}'")
        
        # Initialize git repository if it doesn't exist
        self.git_service.init()
        
    def add_entry(self, category: str, title: str, rating: int, comment: Optional[str] = None) -> None:
        """
        Add a new entry to a stufflog.
        
        Args:
            category: The category name for the stufflog.
            title: The title of the entry.
            rating: The rating for the entry.
            comment: Optional comment for the entry.
            
        Raises:
            StufflogError: If an entry with the same title already exists.
        """
        data = self.load_stufflog(category)
        
        if title in data['Entries']:
            raise StufflogError(f"Entry titled '{title}' already exists in {category} stufflog.")
        
        # Create the new entry
        entry = {
            "Datetime": datetime.datetime.now().isoformat(),
            "Rating": rating
        }
        
        if comment:
            entry["Comment"] = comment
            
        # Add the entry to the data
        data['Entries'][title] = entry
        
        self.save_stufflog(category, data)
        print(f"Added entry '{title}' to {category} stufflog")


def main():
    """Main entry point for the stufflog CLI application."""
    parser = argparse.ArgumentParser(
        description="A general journalling CLI application that uses YAML files."
    )
    
    parser.add_argument(
        "category",
        help="Category for the stufflog (e.g., books, movies)",
        nargs="?",
        default=None
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add cd command (no category needed)
    cd_parser = subparsers.add_parser("cd", help="Open a new shell in the stufflog directory")
    
    # Git command
    git_parser = subparsers.add_parser("git", help="Git repository operations for stufflog")
    git_subparsers = git_parser.add_subparsers(dest="git_command", help="Git command to execute")
    
    # Git init command
    git_init_parser = git_subparsers.add_parser("init", help="Initialize a git repository for stufflog")
    
    # Git remote command
    git_remote_parser = git_subparsers.add_parser("remote", help="Set a remote repository for synchronization")
    git_remote_parser.add_argument("url", help="Remote repository URL (e.g., git@github.com:username/repo.git)")
    git_remote_parser.add_argument("--name", default="origin", help="Name for the remote (default: origin)")
    
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
    search_parser = subparsers.add_parser("search", help="Search for entries containing text")
    search_parser.add_argument("term", help="Text to search for in entry titles and comments")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Create an instance of StufflogApp with GitService dependency
    app = StufflogApp(git_service=GitService())
    
    try:
        # Handle the cd command (no category required)
        if args.command == "cd":
            app.open_stufflog_dir()
            return 0
            
        # Handle the git command (no category required)
        if args.command == "git":
            if args.git_command == "init":
                if app.git_service.init():
                    print("Git repository initialized successfully.")
                    return 0
                else:
                    print("Failed to initialize git repository.", file=sys.stderr)
                    return 1
            elif args.git_command == "remote":
                if app.setup_git_remote(args.url, args.name):
                    return 0
                else:
                    return 1
            else:
                print("Unknown git command.", file=sys.stderr)
                return 1
                
        # All other commands require a category
        if args.category is None:
            print("Category is required for this command.", file=sys.stderr)
            return 1
            
        # Handle the init command
        if args.command == "init":
            app.init_stufflog(args.category)
            return 0
            
        # Handle the add command
        elif args.command == "add":
            app.add_entry(args.category, args.title, args.rating, args.comment)
            return 0
            
        # Handle the query command
        elif args.command == "query":
            entries = app.query_entries(
                args.category,
                args.greater_than,
                args.less_than,
                args.after,
                args.before
            )
            app.display_entries(entries)
            return 0
            
        # Handle the delete command
        elif args.command == "delete":
            app.delete_entry(args.category, args.title)
            return 0
            
        # Handle the search command
        elif args.command == "search":
            entries = app.search_entries(args.category, args.term)
            app.display_entries(entries)
            return 0
            
        # If no command is specified, display the stufflog if it exists
        elif args.command is None:
            try:
                data = app.load_stufflog(args.category)
                entries = [
                    {**entry, "Title": title}
                    for title, entry in data["Entries"].items()
                ]
                app.display_entries(entries)
                return 0
            except StufflogError as e:
                print(str(e), file=sys.stderr)
                return 1
                
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
            
    except StufflogError as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


"""Class for stufflog application."""

VERSION = "0.1.0"

import datetime
import os
import subprocess
from typing import Dict, List, Optional

from stufflog.exceptions import StufflogError
from stufflog.models.query_filters import QueryFilter
from stufflog.services.file_service import FileService
from stufflog.services.git_service import GitService


class StufflogApp:
    """
    A class that encapsulates the functionality of the stufflog application.
    """

    def __init__(
        self,
        git_service: Optional[GitService] = None,
        file_service: Optional[FileService] = None,
    ) -> None:
        """
        Initialize the StufflogApp with optional dependencies.

        Args:
            git_service: The GitService to use for git operations. If None,
                         a new GitService will be created.
            file_service: The FileService to use for file operations. If None,
                         a new FileService will be created.
        """
        self.git_service = git_service or GitService()
        self.file_service = file_service or FileService()

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
        if self.git_service.has_remotes():
            self.git_service.pull()

        file_path = self.file_service.get_stufflog_path(category)

        if not file_path.exists():
            raise StufflogError(
                f"No stufflog found for category '{category}'. "
                f"Use 'stufflog {category} init' to create one."
            )

        try:
            return self.file_service.load_stufflog(category)
        except Exception as e:
            raise StufflogError(f"Error loading stufflog: {e}") from e

    def save_stufflog(self, category: str, data: Dict) -> None:
        """
        Save data to a stufflog file.

        Args:
            category: The category name for the stufflog.
            data: The data to save.
        """
        self.file_service.save_stufflog(category, data)

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

        if title not in data["Entries"]:
            raise StufflogError(
                f"No entry titled '{title}' found in {category} stufflog."
            )

        # Delete the entry
        del data["Entries"][title]

        self.save_stufflog(category, data)
        print(f"Deleted entry '{title}' from {category} stufflog")

    def query_entries(
        self,
        category: str,
        query_filter: Optional[QueryFilter] = None,
    ) -> List[Dict]:
        """
        Query entries in a stufflog based on various filters.

        Args:
            category: The category name for the stufflog.
            query_filter: Filter object containing criteria for filtering entries.

        Returns:
            List[Dict]: A list of entries that match the query criteria.
        """
        data = self.load_stufflog(category)
        results = []

        # Use an empty filter if none provided
        if query_filter is None:
            query_filter = QueryFilter()

        for title, entry in data["Entries"].items():
            # Check if the entry meets all the filter criteria
            include = True

            if (
                query_filter.greater_than is not None
                and entry.get("Rating", 0) <= query_filter.greater_than
            ):
                include = False

            if (
                query_filter.less_than is not None
                and entry.get("Rating", 0) >= query_filter.less_than
            ):
                include = False

            if query_filter.after is not None:
                entry_date = datetime.datetime.fromisoformat(entry.get("Datetime", ""))
                filter_date = datetime.datetime.fromisoformat(query_filter.after)
                if entry_date <= filter_date:
                    include = False

            if query_filter.before is not None:
                entry_date = datetime.datetime.fromisoformat(entry.get("Datetime", ""))
                filter_date = datetime.datetime.fromisoformat(query_filter.before)
                if entry_date >= filter_date:
                    include = False

            if include:
                entry_copy = entry.copy()
                entry_copy["Title"] = title
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
        search_term = (
            search_term.lower()
        )  # Convert to lowercase for case-insensitive search

        for title, entry in data["Entries"].items():
            # Check if the search term is in the title or comment
            title_match = search_term in title.lower()
            comment_match = (
                "Comment" in entry and search_term in entry["Comment"].lower()
            )

            if title_match or comment_match:
                entry_copy = entry.copy()
                entry_copy["Title"] = title
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

            if "Comment" in entry:
                print(f"- **Comment**: {entry['Comment']}")

            print()

    def open_stufflog_dir(self):
        """
        Open a new shell in the stufflog directory.
        """
        stufflog_dir = self.file_service.get_stufflog_dir()
        self.file_service.ensure_stufflog_dir_exists()
        print(f"Opening shell in {stufflog_dir}")

        # Determine the user's shell
        user_shell = os.environ.get("SHELL", "/bin/sh")

        # Open a new shell in the stufflog directory
        try:
            subprocess.run([user_shell], cwd=stufflog_dir, check=True)
        except Exception as e:
            raise StufflogError(f"Failed to open shell: {e}") from e

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
        file_path = self.file_service.get_stufflog_path(category)

        if file_path.exists():
            raise StufflogError(f"Stufflog for category '{category}' already exists.")

        # Initialize with empty data structure
        data = {"Entries": {}}

        self.save_stufflog(category, data)
        print(f"Initialized new stufflog for category '{category}'")

        # Initialize git repository if it doesn't exist
        self.git_service.init()

    def add_entry(
        self, category: str, title: str, rating: int, comment: Optional[str] = None
    ) -> None:
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

        if title in data["Entries"]:
            raise StufflogError(
                f"Entry titled '{title}' already exists in {category} stufflog."
            )

        # Create the new entry
        entry = {"Datetime": datetime.datetime.now().isoformat(), "Rating": rating}

        if comment:
            entry["Comment"] = comment

        # Add the entry to the data
        data["Entries"][title] = entry

        self.save_stufflog(category, data)
        print(f"Added entry '{title}' to {category} stufflog")

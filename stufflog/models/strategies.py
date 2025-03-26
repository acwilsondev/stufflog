"""
This module defines the command strategies for the Stufflog application.
"""

from abc import ABC, abstractmethod
import sys
from stufflog.exceptions import StufflogError
from stufflog.stufflog_app import StufflogApp
from stufflog.models.query_filters import QueryFilter


class CommandStrategy(ABC):
    """
    Abstract base class for command strategies in the Stufflog application.

    This class defines the interface for executing commands within the Stufflog application.
    Subclasses must implement the `execute` method to define specific command behavior.
    """

    @abstractmethod
    def execute(self, app: StufflogApp, args) -> int:
        """
        Executes a command within the Stufflog application.

        Args:
            app (StufflogApp): The instance of the Stufflog application.
            args: The arguments required to execute the command.

        Returns:
            int: The status code resulting from the command execution.
        """


class CdCommandStrategy(CommandStrategy):
    """A command strategy for changing the current directory to the Stufflog directory."""
    def execute(self, app: StufflogApp, args) -> int:
        app.open_stufflog_dir()
        return 0


class GitInitCommandStrategy(CommandStrategy):
    """A command strategy for initializing a git repository."""
    def execute(self, app: StufflogApp, args) -> int:
        if app.git_service.init():
            print("Git repository initialized successfully.")
            return 0
        print("Failed to initialize git repository.", file=sys.stderr)
        return 1


class GitRemoteCommandStrategy(CommandStrategy):
    """A command strategy for setting a remote git repository."""
    def execute(self, app: StufflogApp, args) -> int:
        if app.setup_git_remote(args.url, args.name):
            return 0
        return 1


class InitCommandStrategy(CommandStrategy):
    """A command strategy for initializing the Stufflog directory."""
    def execute(self, app: StufflogApp, args) -> int:
        app.init_stufflog(args.category)
        return 0


class AddCommandStrategy(CommandStrategy):
    """A command strategy for adding an entry to a Stufflog category."""
    def execute(self, app: StufflogApp, args) -> int:
        app.add_entry(args.category, args.title, args.rating, args.comment)
        return 0


class QueryCommandStrategy(CommandStrategy):
    """A command strategy for querying entries in a Stufflog category."""
    def execute(self, app: StufflogApp, args) -> int:
        query_filter = QueryFilter(
            greater_than=args.greater_than,
            less_than=args.less_than,
            after=args.after,
            before=args.before,
        )
        entries = app.query_entries(args.category, query_filter)
        app.display_entries(entries)
        return 0


class DeleteCommandStrategy(CommandStrategy):
    """A command strategy for deleting an entry from a Stufflog category."""
    def execute(self, app: StufflogApp, args) -> int:
        app.delete_entry(args.category, args.title)
        return 0


class SearchCommandStrategy(CommandStrategy):
    """A command strategy for searching entries in a Stufflog category."""
    def execute(self, app: StufflogApp, args) -> int:
        entries = app.search_entries(args.category, args.term)
        app.display_entries(entries)
        return 0


class DefaultCommandStrategy(CommandStrategy):
    """A command strategy for displaying all entries in a Stufflog category."""
    def execute(self, app: StufflogApp, args) -> int:
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

#!/usr/bin/env python3
"""
stufflog - A general journalling CLI application that uses YAML files.

This application allows you to create and manage "stufflogs" for different categories
like books, movies, moods, etc. It stores entries with timestamps, titles, ratings,
and optional comments in human-readable YAML files.
"""

import argparse
import sys
from exceptions import StufflogError
from services.git_service import GitService
from services.file_service import FileService
from models.strategies import (
    CdCommandStrategy,
    GitInitCommandStrategy,
    GitRemoteCommandStrategy,
    InitCommandStrategy,
    AddCommandStrategy,
    QueryCommandStrategy,
    DeleteCommandStrategy,
    SearchCommandStrategy,
    DefaultCommandStrategy,
)
from stufflog_app import StufflogApp


def main():
    """Main entry point for the stufflog CLI application."""
    parser = argparse.ArgumentParser(
        description="A general journalling CLI application that uses YAML files."
    )

    parser.add_argument(
        "category",
        help="Category for the stufflog (e.g., books, movies)",
        nargs="?",
        default=None,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add cd command (no category needed)
    subparsers.add_parser("cd", help="Open a new shell in the stufflog directory")

    # Git command
    git_parser = subparsers.add_parser(
        "git", help="Git repository operations for stufflog"
    )
    git_subparsers = git_parser.add_subparsers(
        dest="git_command", help="Git command to execute"
    )

    # Git init command
    git_subparsers.add_parser("init", help="Initialize a git repository for stufflog")

    # Git remote command
    git_remote_parser = git_subparsers.add_parser(
        "remote", help="Set a remote repository for synchronization"
    )
    git_remote_parser.add_argument(
        "url", help="Remote repository URL (e.g., git@github.com:username/repo.git)"
    )
    git_remote_parser.add_argument(
        "--name", default="origin", help="Name for the remote (default: origin)"
    )

    # Init command
    subparsers.add_parser("init", help="Initialize a new stufflog")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new entry to a stufflog")
    add_parser.add_argument("title", help="Title of the entry")
    add_parser.add_argument("rating", type=int, help="Rating for the entry")
    add_parser.add_argument("comment", nargs="?", help="Optional comment for the entry")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query entries in a stufflog")
    query_parser.add_argument(
        "--greater-than", type=int, help="Filter by rating greater than"
    )
    query_parser.add_argument(
        "--less-than", type=int, help="Filter by rating less than"
    )
    query_parser.add_argument("--after", help="Filter by datetime after (ISO format)")
    query_parser.add_argument("--before", help="Filter by datetime before (ISO format)")

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete", help="Delete an entry from a stufflog"
    )
    delete_parser.add_argument("title", help="Title of the entry to delete")

    # Search command
    search_parser = subparsers.add_parser(
        "search", help="Search for entries containing text"
    )
    search_parser.add_argument(
        "term", help="Text to search for in entry titles and comments"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Create an instance of StufflogApp with GitService dependency
    app = StufflogApp(git_service=GitService(), file_service=FileService())

    # Map commands to their respective strategies
    command_strategies = {
        "cd": CdCommandStrategy(),
        "git_init": GitInitCommandStrategy(),
        "git_remote": GitRemoteCommandStrategy(),
        "init": InitCommandStrategy(),
        "add": AddCommandStrategy(),
        "query": QueryCommandStrategy(),
        "delete": DeleteCommandStrategy(),
        "search": SearchCommandStrategy(),
        None: DefaultCommandStrategy(),
    }

    try:
        if args.command == "git":
            strategy = command_strategies.get(f"git_{args.git_command}")
        else:
            strategy = command_strategies.get(args.command)

        if strategy:
            return strategy.execute(app, args)

        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1

    except StufflogError as e:
        print(str(e), file=sys.stderr)
        return 1
    # top level exception handling, we'll ignore all exceptions
    # pylint: disable=broad-except
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

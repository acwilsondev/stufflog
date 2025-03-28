#!/usr/bin/env python3
"""
git_service - A class to handle git operations for the stufflog application.

This module provides a GitService class that encapsulates git functionality
to enable dependency injection and make testing easier.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


class GitService:
    """
    A class that encapsulates git operations for the stufflog application.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the GitService with a base directory.

        Args:
            base_dir: The directory to use for git operations. If None,
                      it will use the default stufflog directory.
                      Can be a string or Path object.
        """
        if base_dir is None:
            self.base_dir = Path.home() / ".stufflog"
        else:
            self.base_dir = Path(base_dir)

    @property
    def git_dir_path(self) -> Path:
        """
        Get the path to the .git directory in the base directory.

        Returns:
            Path: Path to the .git directory
        """
        base_path = Path(self.base_dir)
        return base_path / ".git"

    def init(self) -> bool:
        """
        Initialize a git repository in the base directory if one doesn't exist.

        Returns:
            bool: True if initialization was successful or already initialized, False otherwise.
        """

        # Check if git is already initialized
        if self.git_dir_path.exists():
            return True

        try:
            # Initialize git repository
            subprocess.run(
                ["git", "init"], cwd=self.base_dir, check=True, capture_output=True
            )

            # Initial commit
            subprocess.run(
                ["git", "add", "."], cwd=self.base_dir, check=True, capture_output=True
            )

            subprocess.run(
                ["git", "commit", "-m", "Initial commit for stufflog"],
                cwd=self.base_dir,
                check=True,
                capture_output=True,
            )

            return True
        except subprocess.CalledProcessError as e:
            print(f"Git initialization failed: {e}", file=sys.stderr)
            return False

    def has_remotes(self) -> bool:
        """
        Check if the git repository has any remotes configured.

        Returns:
            bool: True if remotes are configured, False otherwise.
        """

        # Check if git is initialized
        if not self.git_dir_path.exists():
            return False

        try:
            # Check for remotes
            result = subprocess.run(
                ["git", "remote"],
                cwd=self.base_dir,
                check=True,
                capture_output=True,
                text=True,
            )

            # If there are remotes, the output will not be empty
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def pull(self) -> bool:
        """
        Pull changes from the remote repository.

        Returns:
            bool: True if pull was successful, False otherwise.
        """
        # Check if git is initialized and has remotes
        if not self.has_remotes():
            return False

        try:
            # Pull changes
            subprocess.run(
                ["git", "pull"],
                cwd=self.base_dir,
                check=True,
                capture_output=True,
                text=True,
            )

            return True
        except subprocess.CalledProcessError as e:
            print(f"Git pull failed: {e}", file=sys.stderr)
            return False

    def push(self) -> bool:
        """
        Push changes to the remote repository.

        Returns:
            bool: True if push was successful, False otherwise.
        """
        # Check if git is initialized and has remotes
        if not self.has_remotes():
            return False

        try:
            # Add all changes
            subprocess.run(
                ["git", "add", "."], cwd=self.base_dir, check=True, capture_output=True
            )

            # Commit changes
            try:
                subprocess.run(
                    ["git", "commit", "-m", "Update stufflog entries"],
                    cwd=self.base_dir,
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError:
                # It's ok if commit fails (e.g., no changes)
                pass

            # Push changes
            subprocess.run(
                ["git", "push"], cwd=self.base_dir, check=True, capture_output=True
            )

            return True
        except subprocess.CalledProcessError as e:
            print(f"Git push failed: {e}", file=sys.stderr)
            return False

    def setup_remote(self, remote_url: str, remote_name: str = "origin") -> bool:
        """
        Set up a remote repository for the git repository.

        Args:
            remote_url: URL of the remote repository
            remote_name: Name for the remote (default: origin)

        Returns:
            bool: True if successful, False otherwise
        """
        # Make sure git is initialized
        if not self.init():
            print("Failed to initialize git repository.", file=sys.stderr)
            return False

        try:
            # Add remote
            subprocess.run(
                ["git", "remote", "add", remote_name, remote_url],
                cwd=self.base_dir,
                check=True,
                capture_output=True,
            )

            print(f"Remote '{remote_name}' added successfully.")
            print(
                f"You can now push your stufflog data with: git push -u {remote_name} master"
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to add remote: {e}", file=sys.stderr)
            return False

"""
File service for loading and saving stufflog files.

This module provides a FileService class that handles all file operations
related to stufflog files, including determining directory paths, loading
from files, and saving to files.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class FileService:
    """Service for handling file operations for stufflogs.

    This class encapsulates all file-related functionality, making it easier
    to test the application by allowing the file service to be mocked.

    Attributes:
        base_dir: The base directory for stufflog files
    """

    def __init__(self, base_dir: Optional[str] = None):
        """Initialize the file service with a base directory.

        Args:
            base_dir: The base directory for stufflog files.
                      If None, uses the default location.
        """
        self.base_dir = base_dir

    def get_stufflog_dir(self) -> Path:
        """Get the directory where stufflog files are stored.

        Returns:
            Path: The path to the stufflog directory
        """
        if self.base_dir:
            return Path(self.base_dir)
        
        return Path.home() / ".stufflog"

    def get_stufflog_path(self, name: str) -> Path:
        """Get the full path to a stufflog file.

        Args:
            name: The name of the stufflog

        Returns:
            Path: The full path to the stufflog file
        """
        # Make sure the extension is .yml
        if not name.endswith(".yml"):
            name = f"{name}.yml"
        
        return self.get_stufflog_dir() / name

    def ensure_stufflog_dir_exists(self) -> None:
        """Ensure the stufflog directory exists.

        Creates the directory if it doesn't exist.
        """
        directory = self.get_stufflog_dir()
        directory.mkdir(parents=True, exist_ok=True)

    def load_stufflog(self, name: str) -> Dict[str, Any]:
        """Load a stufflog from the filesystem.

        Args:
            name: The name of the stufflog to load

        Returns:
            The loaded stufflog data as a dictionary

        Raises:
            FileNotFoundError: If the stufflog file doesn't exist
        """
        path = self.get_stufflog_path(name)
        
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
                # Ensure 'Entries' key exists
                # Ensure 'Entries' key exists
                if "Entries" not in data:
                    data["Entries"] = {}
                return data
        except FileNotFoundError:
            # Create an empty stufflog file
            empty_stufflog = {"Entries": {}}
            return empty_stufflog
        except yaml.YAMLError:
            # If the file exists but is empty or invalid YAML, return an empty stufflog
            return {"Entries": {}}
    
    def save_stufflog(self, name: str, data: Dict[str, Any]) -> None:
        """Save a stufflog to the filesystem.

        Args:
            name: The name of the stufflog to save
            data: The stufflog data to save
        """
        self.ensure_stufflog_dir_exists()
        
        path = self.get_stufflog_path(name)
        
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def list_stufflogs(self) -> list[str]:
        """List all available stufflog files.

        Returns:
            A list of stufflog names (without .yml extension)
        """
        directory = self.get_stufflog_dir()
        if not directory.exists():
            return []
            
        stufflogs = []
        for filename in directory.iterdir():
            if filename.name.endswith(".yml"):
                # Remove the .yml extension
                stufflogs.append(filename.name[:-4])
        
        return stufflogs


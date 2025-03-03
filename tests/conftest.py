import os
import shutil
from unittest import mock

import pytest


@pytest.fixture
def stufflog_dir(tmp_path):
    """
    Fixture that creates a temporary directory for stufflog data.
    The fixture initializes the directory structure needed for tests.
    """
    # Create base stufflog directory
    stufflog_temp_dir = tmp_path / "stufflog_test"
    stufflog_temp_dir.mkdir()
    
    # Create subdirectories that stufflog might need
    categories_dir = stufflog_temp_dir / "categories"
    categories_dir.mkdir()
    
    # Set environment variable to point to this directory
    old_home = os.environ.get("HOME")
    os.environ["STUFFLOG_DIR"] = str(stufflog_temp_dir)
    
    yield stufflog_temp_dir
    
    # Cleanup
    if old_home is not None:
        os.environ["HOME"] = old_home
    elif "HOME" in os.environ:
        del os.environ["HOME"]
    if "STUFFLOG_DIR" in os.environ:
        del os.environ["STUFFLOG_DIR"]


@pytest.fixture
def mock_git():
    """
    Fixture that mocks git commands used by stufflog.
    Returns a mock object that can be configured in tests.
    """
    with mock.patch("subprocess.run") as mock_run:
        # Configure mock to return success by default
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        yield mock_run


@pytest.fixture
def mock_git_repo(stufflog_dir):
    """
    Fixture that creates a fake git repository structure in the
    stufflog directory to simulate a git-initialized environment.
    """
    # Create .git directory to simulate a git repo
    git_dir = stufflog_dir / ".git"
    git_dir.mkdir()
    
    # Create minimal git files
    (git_dir / "HEAD").write_text("ref: refs/heads/main")
    
    # Create refs directory
    refs_dir = git_dir / "refs" / "heads"
    refs_dir.mkdir(parents=True)
    (refs_dir / "main").write_text("0" * 40)  # Fake commit hash
    
    yield stufflog_dir
    
    # Cleanup is handled by the stufflog_dir fixture


@pytest.fixture
def mock_git_failure():
    """
    Fixture that mocks git commands to simulate failure.
    """
    with mock.patch("subprocess.run") as mock_run:
        # Configure mock to return failure
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "git error"
        yield mock_run


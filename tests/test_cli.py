import os
import io
import sys
import pytest
from unittest.mock import patch
import subprocess
from contextlib import redirect_stdout

# Import the main module that contains the CLI functions
import stufflog


def test_main_help(capsys):
    """Test that the main help message is displayed correctly."""
    with pytest.raises(SystemExit) as excinfo:
        with patch.object(sys, 'argv', ['stufflog', '--help']):
            stufflog.main()
    
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "A simple, plaintext, command-line, stuff-tracking tool" in captured.out


def test_main_version(capsys):
    """Test that the version command works."""
    with pytest.raises(SystemExit) as excinfo:
        with patch.object(sys, 'argv', ['stufflog', '--version']):
            stufflog.main()
    
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "stufflog version" in captured.out


def test_init_command(stufflog_dir, capsys):
    """Test the init command creates the correct directory structure."""
    with patch.object(sys, 'argv', ['stufflog', 'init']):
        stufflog.main()
    
    # Check that the logs directory was created
    logs_dir = os.path.join(stufflog_dir, 'logs')
    assert os.path.isdir(logs_dir)
    
    # Check the output message
    captured = capsys.readouterr()
    assert f"Initialized stufflog in {stufflog_dir}" in captured.out


def test_init_with_git(stufflog_dir, mock_git, capsys):
    """Test initializing with git enabled."""
    with patch.object(sys, 'argv', ['stufflog', 'init', '--git']):
        stufflog.main()
    
    # Check that git was initialized
    mock_git.assert_called_with(['git', 'init'], check=True, capture_output=True)
    
    captured = capsys.readouterr()
    assert f"Initialized stufflog in {stufflog_dir}" in captured.out
    assert "Initialized git repository" in captured.out


def test_init_with_existing_directory(stufflog_dir, capsys):
    """Test initializing when the directory already exists."""
    # First init to create the directory
    with patch.object(sys, 'argv', ['stufflog', 'init']):
        stufflog.main()
    
    # Try initializing again
    with patch.object(sys, 'argv', ['stufflog', 'init']):
        stufflog.main()
    
    captured = capsys.readouterr()
    assert "Stufflog already initialized" in captured.out


def test_add_command(stufflog_dir, capsys):
    """Test adding an entry to a log."""
    # First init
    with patch.object(sys, 'argv', ['stufflog', 'init']):
        stufflog.main()
    
    # Then add an entry
    with patch.object(sys, 'argv', ['stufflog', 'add', 'books', 'title:The Hobbit', 'author:J.R.R. Tolkien']):
        stufflog.main()
    
    # Check that the log file was created
    log_file = os.path.join(stufflog_dir, 'logs', 'books.yaml')
    assert os.path.isfile(log_file)
    
    # Check the output message
    captured = capsys.readouterr()
    assert "Added entry to books" in captured.out
    
    # Load the log file and check its contents
    with open(log_file, 'r') as f:
        content = f.read()
    assert "title: The Hobbit" in content
    assert "author: J.R.R. Tolkien" in content


def test_add_with_git_commit(stufflog_dir, mock_git, capsys):
    """Test adding an entry with git commit."""
    # First init with git
    with patch.object(sys, 'argv', ['stufflog', 'init', '--git']):
        stufflog.main()
    
    # Then add an entry
    with patch.object(sys, 'argv', ['stufflog', 'add', 'movies', 'title:Inception', 'director:Christopher Nolan']):
        stufflog.main()
    
    # Check that git add and commit were called
    mock_git.assert_any_call(['git', 'add', '.'], check=True, capture_output=True)
    mock_git.assert_any_call(['git', 'commit', '-m', 'Added entry to movies'], check=True, capture_output=True)
    
    captured = capsys.readouterr()
    assert "Added entry to movies" in captured.out
    assert "Committed changes to git" in captured.out


def test_delete_command(stufflog_dir, capsys):
    """Test deleting an entry from a log."""
    # First init
    with patch.object(sys, 'argv', ['stufflog', 'init']):
        stufflog.main()
    
    # Add an entry
    with patch.object(sys, 'argv', ['stufflog', 'add', 'books', 'title:The Hobbit', 'author:J.R.R. Tolkien']):
        stufflog.main()
    
    # Add another entry
    with patch.object(sys, 'argv', ['stufflog', 'add', 'books', 'title:The Lord of the Rings', 'author:J.R.R. Tolkien']):
        stufflog.main()
    
    # Delete the first entry (assuming it's at index 0)
    with patch.object(sys, 'argv', ['stufflog', 'delete', 'books', '0']):
        stufflog.main()
    
    # Check the output message
    captured = capsys.readouterr()
    assert "Deleted entry from books" in captured.out
    
    # Load the log file and check its contents
    log_file = os.path.join(stufflog_dir, 'logs', 'books.yaml')
    with open(log_file, 'r') as f:
        content = f.read()
    assert "title: The Hobbit" not in content
    assert "title: The Lord of the Rings" in content


def test_query_command(stufflog_dir, capsys):
    """Test querying entries from a log."""
    # First init
    with patch.object(sys, 'argv', ['stufflog', 'init']):
        stufflog.main()
    
    # Add entries
    with patch.object(sys, 'argv', ['stufflog', 'add', 'books', 'title:The Hobbit', 'author:J.R.R. Tolkien']):
        stufflog.main()
    
    with patch.object(sys, 'argv', ['stufflog', 'add', 'books', 'title:Dune', 'author:Frank Herbert']):
        stufflog.main()
    
    # Query all entries
    with patch.object(sys, 'argv', ['stufflog', 'query', 'books']):
        with io.StringIO() as buf, redirect_stdout(buf):
            stufflog.main()
            output = buf.getvalue()
    
    # Check that both entries are in the output
    assert "The Hobbit" in output
    assert "J.R.R. Tolkien" in output
    assert "Dune" in output
    assert "Frank Herbert" in output


def test_query_with_filter(stufflog_dir, capsys):
    """Test querying entries with a filter."""
    # First init
    with patch.object(sys, 'argv', ['stufflog', 'init']):
        stufflog.main()
    
    # Add entries
    with patch.object(sys, 'argv', ['stufflog', 'add', 'books', 'title:The Hobbit', 'author:J.R.R. Tolkien']):
        stufflog.main()
    
    with patch.object(sys, 'argv', ['stufflog', 'add', 'books', 'title:Dune', 'author:Frank Herbert']):
        stufflog.main()
    
    # Query with filter
    with patch.object(sys, 'argv', ['stufflog', 'query', 'books', 'author:J.R.R. Tolkien']):
        with io.StringIO() as buf, redirect_stdout(buf):
            stufflog.main()
            output = buf.getvalue()
    
    # Check that only Tolkien's book is in the output
    assert "The Hobbit" in output
    assert "J.R.R. Tolkien" in output
    assert "Dune" not in output
    assert "Frank Herbert" not in output


def test_search_command(stufflog_dir, capsys):
    """Test searching across all logs."""
    # First init
    with patch.object(sys, 'argv', ['stufflog', 'init']):
        stufflog.main()
    
    # Add entries to different logs
    with patch.object(sys, 'argv', ['stufflog', 'add', 'books', 'title:The Hobbit', 'author:J.R.R. Tolkien']):
        stufflog.main()
    
    with patch.object(sys, 'argv', ['stufflog', 'add', 'movies', 'title:The Hobbit', 'director:Peter Jackson']):
        stufflog.main()
    
    # Search for "Hobbit"
    with patch.object(sys, 'argv', ['stufflog', 'search', 'Hobbit']):
        with io.StringIO() as buf, redirect_stdout(buf):
            stufflog.main()
            output = buf.getvalue()
    
    # Check that both entries are found
    assert "books" in output
    assert "movies" in output
    assert "The Hobbit" in output


def test_nonexistent_command(capsys):
    """Test error handling for nonexistent commands."""
    with pytest.raises(SystemExit) as excinfo:
        with patch.object(sys, 'argv', ['stufflog', 'nonexistent']):
            stufflog.main()
    
    assert excinfo.value.code != 0
    captured = capsys.readouterr()
    assert "invalid choice" in captured.err or "unknown command" in captured.err


def test_git_sync_command(stufflog_dir, mock_git, capsys):
    """Test the git sync command."""
    # First init with git
    with patch.object(sys, 'argv', ['stufflog', 'init', '--git']):
        stufflog.main()
    
    # Mock a git remote
    mock_git.return_value.stdout = b"origin\n"
    
    # Then try to sync
    with patch.object(sys, 'argv', ['stufflog', 'git', 'sync']):
        stufflog.main()
    
    # Check git commands were called
    mock_git.assert_any_call(['git', 'pull', '--rebase', 'origin', 'master'], check=True, capture_output=True)
    mock_git.assert_any_call(['git', 'push', 'origin', 'master'], check=True, capture_output=True)
    
    captured = capsys.readouterr()
    assert "Synced with git remote" in captured.out


def test_error_handling(stufflog_dir, capsys):
    """Test error handling when operations fail."""
    # Try to query a nonexistent log
    with pytest.raises(SystemExit) as excinfo:
        with patch.object(sys, 'argv', ['stufflog', 'query', 'nonexistent']):
            stufflog.main()
    
    assert excinfo.value.code != 0
    captured = capsys.readouterr()
    assert "Error" in captured.err or "No such log" in captured.err


if __name__ == '__main__':
    pytest.main()


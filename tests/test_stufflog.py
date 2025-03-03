import os
import datetime
import pytest
import yaml
from pathlib import Path
from unittest import mock

# Import the stufflog functions
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stufflog


class TestStufflog:
    """Tests for the stufflog application."""

    def test_get_stufflog_dir(self, stufflog_dir):
        """Test get_stufflog_dir properly uses environment variable."""
        # Since we used the stufflog_dir fixture, STUFFLOG_DIR should be set
        result = stufflog.get_stufflog_dir()
        assert result == stufflog_dir
        
        # Test with environment variable removed
        if "STUFFLOG_DIR" in os.environ:
            del os.environ["STUFFLOG_DIR"]
        result = stufflog.get_stufflog_dir()
        assert result == Path.home() / '.stufflog'
        
    def test_get_stufflog_path(self, stufflog_dir):
        """Test get_stufflog_path returns the correct path."""
        category = "books"
        expected_path = stufflog_dir / f"{category}.yml"
        
        result = stufflog.get_stufflog_path(category)
        assert result == expected_path
    
    def test_init_stufflog(self, stufflog_dir):
        """Test initializing a new stufflog."""
        category = "movies"
        stufflog.init_stufflog(category)
        
        # Check if the file was created
        file_path = stufflog_dir / f"{category}.yml"
        assert file_path.exists()
        
        # Check if the file has the correct structure
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            assert 'Entries' in data
            assert isinstance(data['Entries'], dict)
            assert len(data['Entries']) == 0
    
    def test_init_stufflog_already_exists(self, stufflog_dir):
        """Test initializing a stufflog that already exists."""
        category = "books"
        
        # Initialize the stufflog first
        stufflog.init_stufflog(category)
        
        # Try to initialize it again, which should raise an error
        with pytest.raises(stufflog.StufflogError) as excinfo:
            stufflog.init_stufflog(category)
        
        assert f"A stufflog with the category '{category}' already exists" in str(excinfo.value)
    
    def test_add_entry(self, stufflog_dir):
        """Test adding an entry to a stufflog."""
        category = "movies"
        title = "The Matrix"
        rating = 5
        comment = "Great sci-fi movie"
        
        # Initialize the stufflog first
        stufflog.init_stufflog(category)
        
        # Add an entry
        stufflog.add_entry(category, title, rating, comment)
        
        # Load the stufflog and check if the entry was added correctly
        file_path = stufflog_dir / f"{category}.yml"
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            
            assert title in data['Entries']
            entry = data['Entries'][title]
            assert entry['Title'] == title
            assert entry['Rating'] == rating
            assert entry['Comment'] == comment
            assert 'Datetime' in entry
    
    def test_add_entry_no_comment(self, stufflog_dir):
        """Test adding an entry without a comment."""
        category = "books"
        title = "1984"
        rating = 4
        
        # Initialize the stufflog first
        stufflog.init_stufflog(category)
        
        # Add an entry without a comment
        stufflog.add_entry(category, title, rating)
        
        # Load the stufflog and check if the entry was added correctly
        file_path = stufflog_dir / f"{category}.yml"
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            
            assert title in data['Entries']
            entry = data['Entries'][title]
            assert entry['Title'] == title
            assert entry['Rating'] == rating
            assert 'Comment' not in entry
    
    def test_add_duplicate_entry(self, stufflog_dir):
        """Test adding an entry with a title that already exists."""
        category = "movies"
        title = "The Matrix"
        rating = 5
        
        # Initialize the stufflog first
        stufflog.init_stufflog(category)
        
        # Add an entry
        stufflog.add_entry(category, title, rating)
        
        # Try to add another entry with the same title
        with pytest.raises(stufflog.StufflogError) as excinfo:
            stufflog.add_entry(category, title, 4)
        
        assert f"An entry titled '{title}' already exists" in str(excinfo.value)
    
    def test_delete_entry(self, stufflog_dir):
        """Test deleting an entry from a stufflog."""
        category = "books"
        title = "1984"
        rating = 4
        
        # Initialize the stufflog and add an entry
        stufflog.init_stufflog(category)
        stufflog.add_entry(category, title, rating)
        
        # Delete the entry
        stufflog.delete_entry(category, title)
        
        # Load the stufflog and check if the entry was deleted
        file_path = stufflog_dir / f"{category}.yml"
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            
            assert title not in data['Entries']
    
    def test_delete_nonexistent_entry(self, stufflog_dir):
        """Test deleting an entry that doesn't exist."""
        category = "movies"
        title = "Nonexistent Movie"
        
        # Initialize the stufflog
        stufflog.init_stufflog(category)
        
        # Try to delete a nonexistent entry
        with pytest.raises(stufflog.StufflogError) as excinfo:
            stufflog.delete_entry(category, title)
        
        assert f"No entry titled '{title}' found in {category} stufflog" in str(excinfo.value)
    
    def test_load_nonexistent_stufflog(self):
        """Test loading a stufflog that doesn't exist."""
        category = "nonexistent"
        
        with pytest.raises(stufflog.StufflogError) as excinfo:
            stufflog.load_stufflog(category)
        
        assert f"No stufflog found for category '{category}'" in str(excinfo.value)
    
    def test_load_stufflog(self, stufflog_dir):
        """Test loading a stufflog."""
        category = "books"
        
        # Initialize the stufflog
        stufflog.init_stufflog(category)
        
        # Load the stufflog
        data = stufflog.load_stufflog(category)
        
        assert 'Entries' in data
        assert isinstance(data['Entries'], dict)
    
    def test_query_entries(self, stufflog_dir):
        """Test querying entries by rating and date."""
        category = "movies"
        
        # Initialize the stufflog
        stufflog.init_stufflog(category)
        
        # Add entries with different ratings and dates
        with mock.patch('datetime.datetime') as mock_datetime:
            # Create fixed datetime for testing
            mock_datetime.now.return_value = datetime.datetime(2023, 1, 1, 12, 0)
            mock_datetime.fromisoformat = datetime.datetime.fromisoformat
            
            stufflog.add_entry(category, "Movie 1", 3, "Average movie")
            
            # Set a different date for the next entry
            mock_datetime.now.return_value = datetime.datetime(2023, 2, 1, 12, 0)
            stufflog.add_entry(category, "Movie 2", 5, "Excellent movie")
            
            # Set a different date for the next entry
            mock_datetime.now.return_value = datetime.datetime(2023, 3, 1, 12, 0)
            stufflog.add_entry(category, "Movie 3", 1, "Bad movie")
        
        # Test querying by rating greater than
        results = stufflog.query_entries(category, greater_than=3)
        assert len(results) == 1
        assert results[0]['Title'] == "Movie 2"
        
        # Test querying by rating less than
        results = stufflog.query_entries(category, less_than=3)
        assert len(results) == 1
        assert results[0]['Title'] == "Movie 3"
        
        # Test querying by date after
        results = stufflog.query_entries(category, after="2023-01-15T00:00:00")
        assert len(results) == 2
        assert results[0]['Title'] == "Movie 2"
        assert results[1]['Title'] == "Movie 3"
        
        # Test querying by date before
        results = stufflog.query_entries(category, before="2023-02-15T00:00:00")
        assert len(results) == 2
        assert results[0]['Title'] == "Movie 1"
        assert results[1]['Title'] == "Movie 2"
        
        # Test combined query
        results = stufflog.query_entries(
            category,
            greater_than=2,
            before="2023-02-15T00:00:00"
        )
        assert len(results) == 1
        assert results[0]['Title'] == "Movie 2"
        
        # Test query with no results
        results = stufflog.query_entries(
            category,
            greater_than=10
        )
        assert len(results) == 0
    
    def test_search_entries(self, stufflog_dir):
        """Test searching entries by text in title or comment."""
        category = "books"
        
        # Initialize the stufflog
        stufflog.init_stufflog(category)
        
        # Add entries with different titles and comments
        stufflog.add_entry(category, "Programming Python", 5, "Great programming book")
        stufflog.add_entry(category, "The C Programming Language", 4, "Classic book")
        stufflog.add_entry(category, "JavaScript: The Good Parts", 4, "Helpful for web development")
        
        # Test searching by text in title
        results = stufflog.search_entries(category, "python")
        assert len(results) == 1
        assert results[0]['Title'] == "Programming Python"
        
        # Test searching by text in title (case-insensitive)
        results = stufflog.search_entries(category, "PYTHON")
        assert len(results) == 1
        assert results[0]['Title'] == "Programming Python"
        
        # Test searching by text in comment
        results = stufflog.search_entries(category, "programming")
        assert len(results) == 2
        assert {results[0]['Title'], results[1]['Title']} == {"Programming Python", "The C Programming Language"}
        
        # Test searching by text in title or comment
        results = stufflog.search_entries(category, "web")
        assert len(results) == 1
        assert results[0]['Title'] == "JavaScript: The Good Parts"
        
        # Test search with no results
        results = stufflog.search_entries(category, "nonexistent")
        assert len(results) == 0
    
    def test_save_stufflog(self, stufflog_dir):
        """Test saving a stufflog to a file."""
        category = "notes"
        
        # Create data to save
        data = {
            'Entries': {
                'Note 1': {
                    'Title': 'Note 1',
                    'Rating': 3,
                    'Datetime': datetime.datetime.now().isoformat()
                }
            }
        }
        
        # Save the stufflog
        stufflog.save_stufflog(category, data)
        
        # Check if the file was created
        file_path = stufflog_dir / f"{category}.yml"
        assert file_path.exists()
        
        # Check if the file contains the correct data
        with open(file_path, 'r') as file:
            loaded_data = yaml.safe_load(file)
            assert loaded_data == data
    
    def test_git_integration(self, stufflog_dir, mock_git, mock_git_repo):
        """Test git integration with stufflog operations."""
        category = "movies"
        
        # Initialize the stufflog
        stufflog.init_stufflog(category)
        
        # Mock git_has_remotes to return True for testing git push
        with mock.patch('stufflog.git_has_remotes', return_value=True):
            # Add an entry (should trigger git push)
            stufflog.add_entry(category, "The Matrix", 5, "Great movie")
            
            # Verify git commands were called
            assert mock_git.call_count > 0
            
            # Find the call to git push
            git_push_call = False
            for call in mock_git.call_args_list:
                args, kwargs = call
                if args and len(args[0]) >= 2 and args[0][1] == "push":
                    git_push_call = True
                    break
            
            assert git_push_call, "git push should have been called"
    
    def test_git_init(self, stufflog_dir, mock_git):
        """Test git initialization."""
        # Call git_init function
        result = stufflog.git_init()
        
        # Verify git init was called
        assert result is True
        mock_git.assert_any_call(
            ["git", "init"],
            cwd=stufflog_dir,
            check=True,
            capture_output=True
        )
    
    def test_git_init_failure(self, stufflog_dir, mock_git_failure):
        """Test git initialization failure."""
        # Call git_init function
        result = stufflog.git_init()
        
        # Verify git init failed
        assert result is False


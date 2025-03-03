#!/usr/bin/env python3
"""
Test file for demonstrating how to use GitService with StufflogApp
and how to create a mock GitService for testing.
"""

import unittest
from unittest.mock import MagicMock, patch
import tempfile
from pathlib import Path
import os
import shutil

from git_service import GitService
from stufflog import StufflogApp, StufflogError


class TestGitServiceIntegration(unittest.TestCase):
    """
    Tests for demonstrating how GitService integrates with StufflogApp.
    """
    
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        os.environ['STUFFLOG_DIR'] = self.temp_dir
        self.git_service = GitService(Path(self.temp_dir))
        self.app = StufflogApp(self.git_service)
    
    def tearDown(self):
        """Clean up temporary directory after testing."""
        shutil.rmtree(self.temp_dir)
        if 'STUFFLOG_DIR' in os.environ:
            del os.environ['STUFFLOG_DIR']
    
    def test_initialization_with_git_service(self):
        """Test initializing StufflogApp with a GitService instance."""
        # Verify that the app is using the provided git_service
        self.assertEqual(self.app.git_service, self.git_service)
        
        # Test initializing a new stufflog (which should initialize git repository)
        category = "books"
        self.app.init_stufflog(category)
        
        # Verify the category file was created
        file_path = Path(self.temp_dir) / f"{category}.yml"
        self.assertTrue(file_path.exists())
        
        # Verify that git was initialized
        git_dir = Path(self.temp_dir) / ".git"
        self.assertTrue(git_dir.exists())
    
    def test_add_entry_with_git_integration(self):
        """Test adding an entry and pushing with git."""
        # Initialize a category
        category = "movies"
        self.app.init_stufflog(category)
        
        # Mock the push method to verify it's called
        original_push = self.git_service.push
        self.git_service.push = MagicMock(return_value=True)
        
        # Mock has_remotes to return True so push is called
        original_has_remotes = self.git_service.has_remotes
        self.git_service.has_remotes = MagicMock(return_value=True)
        
        # Add an entry
        self.app.add_entry(category, "Test Movie", 5, "Great movie!")
        
        # Verify push was called
        self.git_service.push.assert_called_once()
        
        # Restore original methods
        self.git_service.push = original_push
        self.git_service.has_remotes = original_has_remotes


class TestWithMockGitService(unittest.TestCase):
    """
    Tests demonstrating how to use a mock GitService for testing.
    """
    
    def setUp(self):
        """Set up for mock testing."""
        self.temp_dir = tempfile.mkdtemp()
        os.environ['STUFFLOG_DIR'] = self.temp_dir
        
        # Create a mock GitService
        self.mock_git_service = MagicMock(spec=GitService)
        
        # Set default return values for mock methods
        self.mock_git_service.init.return_value = True
        self.mock_git_service.has_remotes.return_value = True
        self.mock_git_service.pull.return_value = True
        self.mock_git_service.push.return_value = True
        self.mock_git_service.setup_remote.return_value = True
        
        # Create StufflogApp with mock GitService
        self.app = StufflogApp(self.mock_git_service)
    
    def tearDown(self):
        """Clean up temporary directory after testing."""
        shutil.rmtree(self.temp_dir)
        if 'STUFFLOG_DIR' in os.environ:
            del os.environ['STUFFLOG_DIR']
    
    def test_init_stufflog_calls_git_init(self):
        """Test that initializing a stufflog calls git init."""
        # Initialize a category
        self.app.init_stufflog("books")
        
        # Verify git init was called
        self.mock_git_service.init.assert_called_once()
    
    def test_load_stufflog_calls_git_pull(self):
        """Test that loading a stufflog calls git pull when remotes exist."""
        # Create a test file first (to avoid StufflogError)
        category = "books"
        file_path = Path(self.temp_dir) / f"{category}.yml"
        with open(file_path, 'w') as f:
            f.write("Entries: {}")
        
        # Load the stufflog
        self.app.load_stufflog(category)
        
        # Verify has_remotes and pull were called
        self.mock_git_service.has_remotes.assert_called_once()
        self.mock_git_service.pull.assert_called_once()
    
    def test_save_stufflog_calls_git_push(self):
        """Test that saving a stufflog calls git push when remotes exist."""
        # Create a test file first (to avoid StufflogError when loading)
        category = "books"
        file_path = Path(self.temp_dir) / f"{category}.yml"
        with open(file_path, 'w') as f:
            f.write("Entries: {}")
        
        # Load and save the stufflog
        data = self.app.load_stufflog(category)
        self.app.save_stufflog(category, data)
        
        # Verify has_remotes and push were called
        self.assertEqual(self.mock_git_service.has_remotes.call_count, 2)  # once for load, once for save
        self.mock_git_service.push.assert_called_once()
    
    def test_setup_git_remote(self):
        """Test setting up a git remote."""
        remote_url = "git@github.com:user/repo.git"
        remote_name = "origin"
        
        # Call setup_git_remote
        result = self.app.setup_git_remote(remote_url, remote_name)
        
        # Verify the result and that setup_remote was called with correct arguments
        self.assertTrue(result)
        self.mock_git_service.setup_remote.assert_called_once_with(remote_url, remote_name)


class TestGitServiceMethodPatching(unittest.TestCase):
    """
    Tests demonstrating how to patch GitService methods directly.
    This approach is useful when you want to use the real StufflogApp 
    but mock specific GitService methods.
    """
    
    def setUp(self):
        """Set up for patching."""
        self.temp_dir = tempfile.mkdtemp()
        os.environ['STUFFLOG_DIR'] = self.temp_dir
        
        # Create a real StufflogApp (which creates a real GitService internally)
        self.app = StufflogApp()
    
    def tearDown(self):
        """Clean up temporary directory after testing."""
        shutil.rmtree(self.temp_dir)
        if 'STUFFLOG_DIR' in os.environ:
            del os.environ['STUFFLOG_DIR']
    
    @patch('git_service.GitService.init')
    def test_patching_git_init(self, mock_init):
        """Test patching the init method of GitService."""
        # Set up the mock to return True
        mock_init.return_value = True
        
        # Initialize a category
        self.app.init_stufflog("books")
        
        # Verify git init was called
        mock_init.assert_called_once()
    
    @patch('git_service.GitService.push')
    @patch('git_service.GitService.has_remotes')
    def test_patching_multiple_methods(self, mock_has_remotes, mock_push):
        """Test patching multiple GitService methods."""
        # Set up mocks
        mock_has_remotes.return_value = True
        mock_push.return_value = True
        
        # Create a test file first (to avoid StufflogError when loading)
        category = "books"
        file_path = Path(self.temp_dir) / f"{category}.yml"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write("Entries: {}")
        
        # Save some data (which should call both has_remotes and push)
        data = {"Entries": {"Test Book": {"Rating": 5}}}
        self.app.save_stufflog(category, data)
        
        # Verify methods were called
        mock_has_remotes.assert_called_once()
        mock_push.assert_called_once()


if __name__ == '__main__':
    unittest.main()


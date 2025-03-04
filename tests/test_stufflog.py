#!/usr/bin/env python3
"""
Tests for StufflogApp using dependency injection to mock both GitService and FileService.

This module demonstrates how to test the StufflogApp in isolation by
mocking its dependencies (GitService and FileService).
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path

from exceptions import StufflogError
from models.query_filters import QueryFilter
from services.git_service import GitService
from services.file_service import FileService
from stufflog_app import StufflogApp


class TestStufflogApp(unittest.TestCase):
    """Test case for StufflogApp with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects for GitService and FileService
        self.mock_git_service = Mock(spec=GitService)
        self.mock_file_service = Mock(spec=FileService)

        # Set up default return values
        self.mock_git_service.has_remotes.return_value = False
        self.mock_file_service.get_stufflog_dir.return_value = Path("/fake/path")

        # Create a test instance of StufflogApp with the mocked services
        self.app = StufflogApp(
            git_service=self.mock_git_service, file_service=self.mock_file_service
        )

        # Sample test data
        self.test_category = "test_category"
        self.test_data = {
            "Entries": {
                "Test Entry 1": {
                    "Datetime": "2023-01-01T12:00:00",
                    "Rating": 5,
                    "Comment": "Test comment 1",
                },
                "Test Entry 2": {"Datetime": "2023-01-02T12:00:00", "Rating": 3},
            }
        }

        self.test_path = Path("/fake/path/test_category.yml")
        self.mock_file_service.get_stufflog_path.return_value = self.test_path

    def test_init_constructor_with_mocks(self):
        """Test that StufflogApp constructor properly accepts mocked dependencies."""
        # Verify that our test instance is using the mocked services
        self.assertIs(self.app.git_service, self.mock_git_service)
        self.assertIs(self.app.file_service, self.mock_file_service)

    def test_load_stufflog_with_git_pull(self):
        """Test loading a stufflog with git pull when remotes are configured."""
        # Configure mocks
        self.mock_git_service.has_remotes.return_value = True
        self.mock_file_service.load_stufflog.return_value = self.test_data

        # Set up path mock to return a path that exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Call the method under test
        result = self.app.load_stufflog(self.test_category)

        # Verify the results and interactions
        self.assertEqual(result, self.test_data)
        self.mock_git_service.pull.assert_called_once()
        self.mock_file_service.get_stufflog_path.assert_called_once_with(
            self.test_category
        )
        self.mock_file_service.load_stufflog.assert_called_once_with(self.test_category)

    def test_load_stufflog_without_git_pull(self):
        """Test loading a stufflog without git pull when no remotes are configured."""
        # Configure mocks
        self.mock_git_service.has_remotes.return_value = False
        self.mock_file_service.load_stufflog.return_value = self.test_data

        # Set up path mock to return a path that exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Call the method under test
        result = self.app.load_stufflog(self.test_category)

        # Verify the results and interactions
        self.assertEqual(result, self.test_data)
        self.mock_git_service.pull.assert_not_called()
        self.mock_file_service.get_stufflog_path.assert_called_once_with(
            self.test_category
        )
        self.mock_file_service.load_stufflog.assert_called_once_with(self.test_category)

    def test_load_stufflog_nonexistent(self):
        """Test loading a nonexistent stufflog raises a StufflogError."""
        # Configure mock to indicate the file doesn't exist
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = False
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Call the method under test and verify it raises the expected error
        with self.assertRaises(StufflogError) as context:
            self.app.load_stufflog(self.test_category)

        # Verify the error message
        self.assertIn(
            f"No stufflog found for category '{self.test_category}'",
            str(context.exception),
        )

        # Verify interactions
        self.mock_file_service.get_stufflog_path.assert_called_once_with(
            self.test_category
        )
        self.mock_file_service.load_stufflog.assert_not_called()

    def test_save_stufflog_with_git_push(self):
        """Test saving a stufflog with git push when remotes are configured."""
        # Configure mocks
        self.mock_git_service.has_remotes.return_value = True

        # Call the method under test
        self.app.save_stufflog(self.test_category, self.test_data)

        # Verify interactions
        self.mock_file_service.save_stufflog.assert_called_once_with(
            self.test_category, self.test_data
        )
        self.mock_git_service.push.assert_called_once()

    def test_save_stufflog_without_git_push(self):
        """Test saving a stufflog without git push when no remotes are configured."""
        # Configure mocks
        self.mock_git_service.has_remotes.return_value = False

        # Call the method under test
        self.app.save_stufflog(self.test_category, self.test_data)

        # Verify interactions
        self.mock_file_service.save_stufflog.assert_called_once_with(
            self.test_category, self.test_data
        )
        self.mock_git_service.push.assert_not_called()

    def test_init_stufflog(self):
        """Test initializing a new stufflog."""
        # Configure mocks
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = False
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Call the method under test
        self.app.init_stufflog(self.test_category)

        # Verify interactions
        self.mock_file_service.get_stufflog_path.assert_called_once_with(
            self.test_category
        )
        self.mock_file_service.save_stufflog.assert_called_once()

        # Verify the data saved
        saved_data = self.mock_file_service.save_stufflog.call_args[0][1]
        self.assertEqual(saved_data, {"Entries": {}})

        # Verify git was initialized
        self.mock_git_service.init.assert_called_once()

    def test_init_stufflog_existing(self):
        """Test initializing a stufflog that already exists raises a StufflogError."""
        # Configure mock to indicate the file already exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Call the method under test and verify it raises the expected error
        with self.assertRaises(StufflogError) as context:
            self.app.init_stufflog(self.test_category)

        # Verify the error message
        self.assertIn(
            f"Stufflog for category '{self.test_category}' already exists",
            str(context.exception),
        )

        # Verify interactions
        self.mock_file_service.save_stufflog.assert_not_called()
        self.mock_git_service.init.assert_not_called()

    def test_add_entry(self):
        """Test adding a new entry to a stufflog."""
        # Configure mocks for loading and saving
        self.mock_file_service.load_stufflog.return_value = {"Entries": {}}

        # Set up path mock to return a path that exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Test data
        title = "New Entry"
        rating = 4
        comment = "Test comment"

        # Call the method under test
        self.app.add_entry(self.test_category, title, rating, comment)

        # Verify interactions
        self.mock_file_service.load_stufflog.assert_called_once_with(self.test_category)
        self.mock_file_service.save_stufflog.assert_called_once()

        # Verify the data saved
        saved_data = self.mock_file_service.save_stufflog.call_args[0][1]
        self.assertEqual(saved_data["Entries"][title]["Rating"], rating)
        self.assertEqual(saved_data["Entries"][title]["Comment"], comment)
        self.assertIn("Datetime", saved_data["Entries"][title])

    def test_add_entry_duplicate(self):
        """Test adding a duplicate entry raises a StufflogError."""
        # Configure mocks for loading
        existing_title = "Existing Entry"
        self.mock_file_service.load_stufflog.return_value = {
            "Entries": {
                existing_title: {"Datetime": "2023-01-01T12:00:00", "Rating": 5}
            }
        }

        # Set up path mock to return a path that exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Call the method under test and verify it raises the expected error
        with self.assertRaises(StufflogError) as context:
            self.app.add_entry(self.test_category, existing_title, 4)

        # Verify the error message
        self.assertIn(
            f"Entry titled '{existing_title}' already exists", str(context.exception)
        )

        # Verify interactions
        self.mock_file_service.load_stufflog.assert_called_once_with(self.test_category)
        self.mock_file_service.save_stufflog.assert_not_called()

    def test_delete_entry(self):
        """Test deleting an entry from a stufflog."""
        # Existing entry to delete
        existing_title = "Entry to Delete"

        # Configure mocks for loading
        self.mock_file_service.load_stufflog.return_value = {
            "Entries": {
                existing_title: {"Datetime": "2023-01-01T12:00:00", "Rating": 5},
                "Other Entry": {"Datetime": "2023-01-02T12:00:00", "Rating": 3},
            }
        }

        # Set up path mock to return a path that exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Call the method under test
        self.app.delete_entry(self.test_category, existing_title)

        # Verify interactions
        self.mock_file_service.load_stufflog.assert_called_once_with(self.test_category)
        self.mock_file_service.save_stufflog.assert_called_once()

        # Verify the data saved
        saved_data = self.mock_file_service.save_stufflog.call_args[0][1]
        self.assertNotIn(existing_title, saved_data["Entries"])
        self.assertIn("Other Entry", saved_data["Entries"])

    def test_delete_entry_nonexistent(self):
        """Test deleting a nonexistent entry raises a StufflogError."""
        # Configure mocks for loading
        self.mock_file_service.load_stufflog.return_value = {
            "Entries": {
                "Existing Entry": {"Datetime": "2023-01-01T12:00:00", "Rating": 5}
            }
        }

        # Set up path mock to return a path that exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Nonexistent entry
        nonexistent_title = "Nonexistent Entry"

        # Call the method under test and verify it raises the expected error
        with self.assertRaises(StufflogError) as context:
            self.app.delete_entry(self.test_category, nonexistent_title)

        # Verify the error message
        self.assertIn(
            f"No entry titled '{nonexistent_title}' found", str(context.exception)
        )

        # Verify interactions
        self.mock_file_service.load_stufflog.assert_called_once_with(self.test_category)
        self.mock_file_service.save_stufflog.assert_not_called()

    def test_query_entries(self):
        """Test querying entries with filters."""
        # Configure mocks for loading
        self.mock_file_service.load_stufflog.return_value = {
            "Entries": {
                "Entry 1": {"Datetime": "2023-01-01T12:00:00", "Rating": 5},
                "Entry 2": {"Datetime": "2023-01-02T12:00:00", "Rating": 3},
                "Entry 3": {"Datetime": "2023-01-03T12:00:00", "Rating": 4},
            }
        }

        # Set up path mock to return a path that exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Test 1: Filter by rating greater than 3
        results = self.app.query_entries(self.test_category, QueryFilter(greater_than=3))
        self.assertEqual(len(results), 2)  # Should include Entry 1 and Entry 3
        titles = [entry["Title"] for entry in results]
        self.assertIn("Entry 1", titles)
        self.assertIn("Entry 3", titles)
        self.assertNotIn("Entry 2", titles)

        # Test 2: Filter by rating less than 5
        results = self.app.query_entries(self.test_category, QueryFilter(less_than=5))
        self.assertEqual(len(results), 2)  # Should include Entry 2 and Entry 3
        titles = [entry["Title"] for entry in results]
        self.assertIn("Entry 2", titles)
        self.assertIn("Entry 3", titles)
        self.assertNotIn("Entry 1", titles)

        # Test 3: Filter by date after 2023-01-01
        results = self.app.query_entries(
            self.test_category, QueryFilter(after="2023-01-01T12:00:00")
        )
        self.assertEqual(len(results), 2)  # Should include Entry 2 and Entry 3
        titles = [entry["Title"] for entry in results]
        self.assertIn("Entry 2", titles)
        self.assertIn("Entry 3", titles)
        self.assertNotIn("Entry 1", titles)

        # Test 4: Filter by date before 2023-01-03
        results = self.app.query_entries(
            self.test_category, QueryFilter(before="2023-01-03T12:00:00")
        )
        self.assertEqual(len(results), 2)  # Should include Entry 1 and Entry 2
        titles = [entry["Title"] for entry in results]
        self.assertIn("Entry 1", titles)
        self.assertIn("Entry 2", titles)
        self.assertNotIn("Entry 3", titles)

        # Test 5: Combined filters (rating > 3 and before 2023-01-03)
        results = self.app.query_entries(
            self.test_category, QueryFilter(greater_than=3, before="2023-01-03T12:00:00")
        )
        self.assertEqual(len(results), 1)  # Should only include Entry 1
        self.assertEqual(results[0]["Title"], "Entry 1")

        # Verify interactions
        self.assertEqual(self.mock_file_service.load_stufflog.call_count, 5)

    def test_search_entries(self):
        """Test searching for entries with a search term."""
        # Configure mocks for loading
        self.mock_file_service.load_stufflog.return_value = {
            "Entries": {
                "Fantasy Book": {
                    "Datetime": "2023-01-01T12:00:00",
                    "Rating": 5,
                    "Comment": "Great fantasy novel with dragons.",
                },
                "Science Fiction": {
                    "Datetime": "2023-01-02T12:00:00",
                    "Rating": 4,
                    "Comment": "Interesting space adventure.",
                },
                "History Book": {
                    "Datetime": "2023-01-03T12:00:00",
                    "Rating": 3,
                    "Comment": "Detailed historical account of medieval times.",
                },
            }
        }

        # Set up path mock to return a path that exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        self.mock_file_service.get_stufflog_path.return_value = mock_path

        # Test 1: Search for "fantasy" in title
        results = self.app.search_entries(self.test_category, "fantasy")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["Title"], "Fantasy Book")

        # Test 2: Search for "dragons" in comment
        results = self.app.search_entries(self.test_category, "dragons")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["Title"], "Fantasy Book")

        # Test 3: Search for "book" in title (should match two entries)
        results = self.app.search_entries(self.test_category, "book")
        self.assertEqual(len(results), 2)
        titles = [entry["Title"] for entry in results]
        self.assertIn("Fantasy Book", titles)
        self.assertIn("History Book", titles)

        # Test 4: Search for non-existent term
        results = self.app.search_entries(self.test_category, "nonexistent")
        self.assertEqual(len(results), 0)

        # Verify interactions
        self.assertEqual(self.mock_file_service.load_stufflog.call_count, 4)

    def test_display_entries(self):
        """Test displaying entries."""
        entries = [
            {
                "Title": "Test Entry",
                "Datetime": "2023-01-01T12:00:00",
                "Rating": 5,
                "Comment": "Test comment",
            }
        ]

        # Test with entries
        with patch("builtins.print") as mock_print:
            self.app.display_entries(entries)
            self.assertTrue(mock_print.called)

        # Test with no entries
        with patch("builtins.print") as mock_print:
            self.app.display_entries([])
            mock_print.assert_called_with("No matching entries found.")

    def test_integration_with_real_services(self):
        """Test StufflogApp with real services in a controlled environment."""
        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create real services with the temp directory
            file_service = FileService(base_dir=temp_dir)
            git_service = GitService(base_dir=temp_dir)

            # Create StufflogApp with real services
            app = StufflogApp(git_service=git_service, file_service=file_service)

            # Test initialization of a new stufflog
            app.init_stufflog("test")

            # Verify the file was created
            test_path = Path(temp_dir) / "test.yml"
            self.assertTrue(test_path.exists())

            # Test adding an entry
            app.add_entry("test", "Test Entry", 5, "Test comment")

            # Test querying
            entries = app.query_entries("test", QueryFilter(greater_than=4))
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["Title"], "Test Entry")


if __name__ == "__main__":
    unittest.main()

import os
import unittest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import yaml

from services.file_service import FileService

class TestFileService(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.file_service = FileService(base_dir=self.test_dir)
        
        # Create test data
        self.test_data = {
            "Entries": [
                {"content": "Test entry 1", "timestamp": "2023-01-01T10:00:00"},
                {"content": "Test entry 2", "timestamp": "2023-01-02T10:00:00"}
            ]
        }
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_get_stufflog_dir(self):
        """Test that get_stufflog_dir returns the correct directory."""
        expected_dir = self.test_dir
        actual_dir = self.file_service.get_stufflog_dir()
        self.assertEqual(expected_dir, actual_dir)

    def test_get_stufflog_path(self):
        """Test that get_stufflog_path returns the correct file path."""
        log_name = "test_log"
        expected_path = self.test_dir / f"{log_name}.yml"
        actual_path = self.file_service.get_stufflog_path(log_name)
        self.assertEqual(expected_path, actual_path)

    def test_save_and_load_stufflog(self):
        """Test saving and loading a stufflog file."""
        log_name = "test_log"
        
        # Save the test data
        self.file_service.save_stufflog(log_name, self.test_data)
        
        # Verify the file exists
        file_path = self.file_service.get_stufflog_path(log_name)
        self.assertTrue(file_path.exists())
        
        # Load the data and verify it matches the original
        loaded_data = self.file_service.load_stufflog(log_name)
        self.assertEqual(self.test_data, loaded_data)

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist returns empty structure."""
        log_name = "nonexistent_log"
        
        # Load a non-existent file
        data = self.file_service.load_stufflog(log_name)
        
        # Verify it returns an empty structure with 'Entries' key
        self.assertEqual({"Entries": {}}, data)

    def test_list_stufflogs(self):
        """Test listing all stufflog files."""
        # Create a few test logs
        test_logs = ["log1", "log2", "log3"]
        for log_name in test_logs:
            self.file_service.save_stufflog(log_name, self.test_data)
        
        # Get the list of logs
        logs = self.file_service.list_stufflogs()
        
        # Verify all test logs are in the list
        for log_name in test_logs:
            self.assertIn(log_name, logs)
        
        # Verify the length matches (only the test logs should be there)
        self.assertEqual(len(test_logs), len(logs))


class TestFileServiceMocking(unittest.TestCase):
    """Tests demonstrating how to mock the FileService."""
    
    def test_with_mock_file_service(self):
        """Test how to use a mock FileService."""
        # Create a mock FileService
        mock_file_service = MagicMock(spec=FileService)
        
        # Set up the mock to return specific values
        mock_file_service.list_stufflogs.return_value = ["log1", "log2"]
        mock_file_service.load_stufflog.return_value = {
            "Entries": [{"content": "Mocked entry", "timestamp": "2023-01-01T12:00:00"}]
        }
        
        # Verify the mock returns the expected values
        self.assertEqual(["log1", "log2"], mock_file_service.list_stufflogs())
        self.assertEqual(
            {"Entries": [{"content": "Mocked entry", "timestamp": "2023-01-01T12:00:00"}]},
            mock_file_service.load_stufflog("any_log")
        )
        
        # Verify the mock was called with the expected arguments
        mock_file_service.load_stufflog.assert_called_with("any_log")

    def test_with_patched_methods(self):
        """Test using patch to mock specific methods."""
        file_service = FileService()
        
        # Create test data
        test_data = {
            "Entries": [
                {"content": "Patched entry", "timestamp": "2023-01-03T10:00:00"}
            ]
        }
        
        # Use patch as a context manager to mock save_stufflog
        with patch.object(file_service, 'save_stufflog') as mock_save:
            file_service.save_stufflog("patched_log", test_data)
            # Verify save_stufflog was called with correct arguments
            mock_save.assert_called_once_with("patched_log", test_data)


if __name__ == "__main__":
    unittest.main()


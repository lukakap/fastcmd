import os
import tempfile
from argparse import Namespace
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from src.commands import handle_add, handle_search


class TestAddCommand:

    @pytest.fixture
    def temp_db_path(self) -> Generator[str, None, None]:
        """Create a temporary database file path for testing."""
        with tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        ) as temp_file:
            temp_db_path = temp_file.name

        # Set the test database path
        from src.vector_database import TEST_DB_PATH

        original_test_db_path = TEST_DB_PATH
        import src.vector_database

        src.vector_database.TEST_DB_PATH = temp_db_path

        yield temp_db_path

        # Reset the test database path
        src.vector_database.TEST_DB_PATH = original_test_db_path

        # Clean up after tests
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)

    def test_add_command_success(self, temp_db_path: str) -> None:
        # Arrange
        args = Namespace(description="List all files", commandrun="ls -la")
        mock_embedding = [0.1] * 1536

        # Act
        with patch(
            "src.commands.calculate_embedding", return_value=mock_embedding
        ) as mock_calc_embedding:
            with patch("src.commands.fastcmd_print") as mock_print:
                result = handle_add(args)

        # Assert
        mock_calc_embedding.assert_called_once_with("List all files")
        mock_print.assert_called_once()
        assert result is True

    def test_add_command_handles_exception(self, temp_db_path: str) -> None:
        # Arrange
        args = Namespace(description="List all files", commandrun="ls -la")

        # Act
        with patch(
            "src.commands.calculate_embedding",
            side_effect=Exception("Test error"),
        ) as mock_calc_embedding:
            with patch("src.commands.fastcmd_print") as mock_print:
                result = handle_add(args)

        # Assert
        mock_calc_embedding.assert_called_once()
        mock_print.assert_called_once()
        assert "Error adding command" in mock_print.call_args[0][0]
        assert result is False


class TestSearchCommand:

    @pytest.fixture
    def temp_db_path(self) -> Generator[str, None, None]:
        """Create a temporary database file path for testing."""
        with tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        ) as temp_file:
            temp_db_path = temp_file.name

        # Set the test database path
        from src.vector_database import TEST_DB_PATH

        original_test_db_path = TEST_DB_PATH
        import src.vector_database

        src.vector_database.TEST_DB_PATH = temp_db_path

        yield temp_db_path

        # Reset the test database path
        src.vector_database.TEST_DB_PATH = original_test_db_path

        # Clean up after tests
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)

    def test_search_command_no_results(self, temp_db_path: str) -> None:
        # Arrange
        args = Namespace(description="Find non-existent command")
        mock_embedding = [0.1] * 1536

        # Act
        with patch(
            "src.commands.calculate_embedding", return_value=mock_embedding
        ) as mock_calc_embedding:
            with patch(
                "src.commands.fetch_similar", return_value=[]
            ) as mock_fetch:
                with patch("src.commands.fastcmd_print") as mock_print:
                    result = handle_search(args)

        # Assert
        mock_calc_embedding.assert_called_once_with(
            "Find non-existent command"
        )
        mock_fetch.assert_called_once_with(mock_embedding, top_k=1)
        assert "No matching commands found" in mock_print.call_args[0][0]
        assert result is False

    def test_search_command_found_but_canceled(
        self, temp_db_path: str
    ) -> None:
        # Arrange
        args = Namespace(description="Find existing command")
        mock_embedding = [0.1] * 1536
        mock_results = [
            {
                "command": "ls -la",
                "description": "List all files",
                "distance": 0.1,
            }
        ]

        # Act
        with patch(
            "src.commands.calculate_embedding", return_value=mock_embedding
        ) as mock_calc_embedding:
            with patch(
                "src.commands.fetch_similar", return_value=mock_results
            ) as mock_fetch:
                with patch("src.commands.fastcmd_print") as mock_print:
                    with patch("src.commands.get_user_input", return_value=""):
                        result = handle_search(args)

        # Assert
        mock_calc_embedding.assert_called_once()
        mock_fetch.assert_called_once_with(mock_embedding, top_k=1)
        assert mock_print.call_count >= 3  # Multiple print calls
        assert "Operation cancelled" in mock_print.call_args[0][0]
        assert result is False

    def test_search_command_execute_success(self, temp_db_path: str) -> None:
        # Arrange
        args = Namespace(description="Find existing command")
        mock_embedding = [0.1] * 1536
        mock_results = [
            {
                "command": "echo hello",
                "description": "Print hello",
                "distance": 0.1,
            }
        ]

        # Mock successful command execution
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "hello\n"

        # Act
        with patch(
            "src.commands.calculate_embedding", return_value=mock_embedding
        ):
            with patch(
                "src.commands.fetch_similar", return_value=mock_results
            ):
                with patch("src.commands.fastcmd_print"):
                    with patch(
                        "src.commands.get_user_input", return_value="1"
                    ):
                        with patch(
                            "subprocess.run", return_value=mock_process
                        ) as mock_run:
                            result = handle_search(args)

        # Assert
        mock_run.assert_called_once_with(
            "echo hello", shell=True, capture_output=True, text=True
        )
        assert result is True

    def test_search_command_execution_failure(self, temp_db_path: str) -> None:
        # Arrange
        args = Namespace(description="Find existing command")
        mock_embedding = [0.1] * 1536
        mock_results = [
            {
                "command": "invalid_command",
                "description": "Invalid command",
                "distance": 0.1,
            }
        ]

        # Mock failed command execution
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "command not found"

        # Act
        with patch(
            "src.commands.calculate_embedding", return_value=mock_embedding
        ):
            with patch(
                "src.commands.fetch_similar", return_value=mock_results
            ):
                with patch("src.commands.fastcmd_print") as mock_print:
                    with patch(
                        "src.commands.get_user_input", return_value="1"
                    ):
                        with patch(
                            "subprocess.run", return_value=mock_process
                        ):
                            result = handle_search(args)

        # Assert
        assert "Command failed with error" in mock_print.call_args[0][0]
        assert result is False

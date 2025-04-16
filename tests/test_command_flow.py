import os
import tempfile
from argparse import Namespace
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from src.commands import handle_add, handle_search
from src.vector_database import init_db


class TestCommandFlow:

    @pytest.fixture
    def temp_db_path(self) -> Generator[str, None, None]:
        """Create a temporary database file for testing the flow."""
        with tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        ) as temp_file:
            temp_db_path = temp_file.name

        # Set the test database path
        from src.vector_database import TEST_DB_PATH

        original_test_db_path = TEST_DB_PATH
        import src.vector_database

        src.vector_database.TEST_DB_PATH = temp_db_path

        # Initialize the database
        init_db()
        yield temp_db_path

        # Reset the test database path
        src.vector_database.TEST_DB_PATH = original_test_db_path

        # Clean up after tests
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)

    def test_add_then_search_flow(self, temp_db_path: str) -> None:
        """Test a complete flow of adding a command then searching for it."""
        # Setup mock embeddings
        mock_embedding1 = [0.1] * 1536
        mock_embedding2 = [
            0.11
        ] * 1536  # Slightly different to ensure it's a close match

        # 1. First add a command
        add_args = Namespace(
            description="List files in color format",
            commandrun="ls --color=auto",
        )

        with patch(
            "src.commands.calculate_embedding", return_value=mock_embedding1
        ):
            result_add = handle_add(add_args)

        # Verify command was added successfully
        assert result_add is True

        # 2. Then search for a similar command
        search_args = Namespace(description="Show files with colors")

        # Mock process for command execution
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "file1.txt  file2.txt\n"

        with patch(
            "src.commands.calculate_embedding", return_value=mock_embedding2
        ):
            with patch(
                "src.commands.get_user_input", return_value="y"
            ):  # User confirms execution with 'y'
                with patch(
                    "subprocess.run", return_value=mock_process
                ) as mock_run:
                    result_search = handle_search(search_args)

        # Verify search and execution were successful
        assert result_search is True
        mock_run.assert_called_once_with(
            "ls --color=auto", shell=True, capture_output=True, text=True
        )

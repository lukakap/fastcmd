import json
import os
import tempfile
from argparse import Namespace
from pathlib import Path
from typing import Any, Generator
from unittest.mock import patch

import pytest

from src.commands import (
    handle_add,
    handle_export,
    handle_import,
    handle_search,
)


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

    def test_search_command_found_and_prints_match(
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
                # Patch print_command_match in src.commands, not src.utils
                with patch(
                    "src.commands.print_command_match"
                ) as mock_print_match:
                    result = handle_search(args)

        # Assert
        mock_calc_embedding.assert_called_once()
        mock_fetch.assert_called_once_with(mock_embedding, top_k=1)
        mock_print_match.assert_called_once()
        assert result is True


class TestExportImportCommands:
    def test_export_command_success(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        # Arrange
        args_add = Namespace(description="List files", commandrun="ls -l")
        handle_add(args_add)
        export_path = tmp_path / "exported.json"
        args_export = Namespace(output=str(export_path))
        # Act
        with monkeypatch.context() as m:
            m.setenv("HOST_HOME", str(tmp_path))
            m.setenv("USER_HOME", str(tmp_path))
            with patch("src.commands.fastcmd_print") as mock_print:
                result = handle_export(args_export)
        # Assert
        assert result is True
        assert export_path.exists()
        with open(export_path) as f:
            data = f.read()
            assert "List files" in data
        assert any(
            "exported" in str(call[0][0]) for call in mock_print.call_args_list
        )

    def test_export_command_empty_db(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        # Arrange
        args_export = Namespace(output=str(tmp_path / "exported.json"))
        # Act
        with monkeypatch.context() as m:
            m.setenv("HOST_HOME", str(tmp_path))
            m.setenv("USER_HOME", str(tmp_path))
            with patch("src.commands.fetch_all_commands", return_value=[]):
                with patch("src.commands.fastcmd_print") as mock_print:
                    result = handle_export(args_export)
        # Assert
        assert result is False
        assert any(
            "No commands found" in str(call[0][0])
            for call in mock_print.call_args_list
        )

    def test_import_command_success(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        # Arrange
        import_path = tmp_path / "import.json"
        commands_data = {
            "commands": [
                {"description": "Echo hello", "command": "echo hello"}
            ]
        }
        with open(import_path, "w") as f:
            json.dump(commands_data, f)
        args_import = Namespace(input=str(import_path))
        # Act
        with monkeypatch.context() as m:
            m.setenv("HOST_HOME", str(tmp_path))
            m.setenv("USER_HOME", str(tmp_path))
            with patch(
                "src.commands.calculate_embedding", return_value=[0.1] * 1536
            ):
                with patch("src.commands.fastcmd_print") as mock_print:
                    result = handle_import(args_import)
        # Assert
        assert result is True
        assert any(
            "Imported 1 commands" in str(call[0][0])
            for call in mock_print.call_args_list
        )

    def test_import_command_file_not_found(
        self, tmp_path: Path, monkeypatch: Any
    ) -> None:
        # Arrange
        missing_path = tmp_path / "missing.json"
        args_import = Namespace(input=str(missing_path))
        # Act
        with monkeypatch.context() as m:
            m.setenv("HOST_HOME", str(tmp_path))
            m.setenv("USER_HOME", str(tmp_path))
            with patch("src.commands.fastcmd_print") as mock_print:
                result = handle_import(args_import)
        # Assert
        assert result is False
        assert any(
            "File not found" in str(call[0][0])
            for call in mock_print.call_args_list
        )

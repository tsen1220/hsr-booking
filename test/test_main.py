import pytest
from unittest.mock import Mock, patch
from src.main import main


class TestMain:
    """Test cases for main module."""

    def test_main_function(self, capsys):
        """Test main function creates and runs assistant."""
        with patch('src.main.BookingAssistant') as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant_class.return_value = mock_assistant

            main()

            mock_assistant_class.assert_called_once()
            mock_assistant.run.assert_called_once()

            captured = capsys.readouterr()
            assert "Starting HSR Booking Assistant..." in captured.out
            assert "Assistant finished." in captured.out

    def test_main_function_assistant_run_exception(self, capsys):
        """Test main function when assistant.run raises an exception."""
        with patch('src.main.BookingAssistant') as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.run.side_effect = Exception("Assistant error")
            mock_assistant_class.return_value = mock_assistant

            with pytest.raises(Exception, match="Assistant error"):
                main()

            mock_assistant_class.assert_called_once()
            mock_assistant.run.assert_called_once()

    def test_main_function_value_error(self, capsys):
        """Test main function when ValueError is raised (time format error)."""
        with patch('src.main.BookingAssistant') as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.run.side_effect = ValueError("Invalid trigger time format")
            mock_assistant_class.return_value = mock_assistant

            result = main()

            assert result == 1
            mock_assistant_class.assert_called_once()
            mock_assistant.run.assert_called_once()

            captured = capsys.readouterr()
            assert "Error:" in captured.out
            assert "Invalid trigger time format" in captured.out

    def test_main_function_keyboard_interrupt(self, capsys):
        """Test main function when KeyboardInterrupt is raised (Ctrl+C)."""
        with patch('src.main.BookingAssistant') as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.run.side_effect = KeyboardInterrupt()
            mock_assistant_class.return_value = mock_assistant

            result = main()

            assert result == 0
            mock_assistant_class.assert_called_once()
            mock_assistant.run.assert_called_once()

            captured = capsys.readouterr()
            assert "Cancelled by user" in captured.out

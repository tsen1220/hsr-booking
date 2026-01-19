import pytest
from unittest.mock import Mock, patch, mock_open
from src.captcha import CaptchaSolver


class TestCaptchaSolver:
    """Test cases for CaptchaSolver class."""

    def test_init(self):
        """Test CaptchaSolver initialization."""
        with patch('src.captcha.ddddocr.DdddOcr') as mock_ocr:
            solver = CaptchaSolver()
            mock_ocr.assert_called_once()
            assert solver.ocr is not None

    def test_solve_bytes_success(self, sample_image_bytes):
        """Test solve_bytes with successful OCR."""
        with patch('src.captcha.ddddocr.DdddOcr') as mock_ocr_class:
            mock_ocr = Mock()
            mock_ocr.classification.return_value = "ABC123"
            mock_ocr_class.return_value = mock_ocr

            solver = CaptchaSolver()
            result = solver.solve_bytes(sample_image_bytes)

            assert result == "ABC123"
            mock_ocr.classification.assert_called_once_with(sample_image_bytes)

    def test_solve_bytes_exception(self, sample_image_bytes, capsys):
        """Test solve_bytes when OCR raises an exception."""
        with patch('src.captcha.ddddocr.DdddOcr') as mock_ocr_class:
            mock_ocr = Mock()
            mock_ocr.classification.side_effect = Exception("OCR failed")
            mock_ocr_class.return_value = mock_ocr

            solver = CaptchaSolver()
            result = solver.solve_bytes(sample_image_bytes)

            assert result == ""
            captured = capsys.readouterr()
            assert "OCR Error: OCR failed" in captured.out

    def test_solve_file_success(self, temp_image_file):
        """Test solve_file with successful file read and OCR."""
        with patch('src.captcha.ddddocr.DdddOcr') as mock_ocr_class:
            mock_ocr = Mock()
            mock_ocr.classification.return_value = "XYZ789"
            mock_ocr_class.return_value = mock_ocr

            solver = CaptchaSolver()
            result = solver.solve_file(temp_image_file)

            assert result == "XYZ789"
            mock_ocr.classification.assert_called_once()

    def test_solve_file_with_bytes_exception(self, temp_image_file, capsys):
        """Test solve_file when OCR fails on bytes."""
        with patch('src.captcha.ddddocr.DdddOcr') as mock_ocr_class:
            mock_ocr = Mock()
            mock_ocr.classification.side_effect = Exception("Classification error")
            mock_ocr_class.return_value = mock_ocr

            solver = CaptchaSolver()
            result = solver.solve_file(temp_image_file)

            assert result == ""
            captured = capsys.readouterr()
            assert "OCR Error: Classification error" in captured.out

    def test_solve_file_file_not_found(self):
        """Test solve_file with non-existent file."""
        with patch('src.captcha.ddddocr.DdddOcr') as mock_ocr_class:
            mock_ocr_class.return_value = Mock()

            solver = CaptchaSolver()
            with pytest.raises(FileNotFoundError):
                solver.solve_file("/nonexistent/path/image.png")

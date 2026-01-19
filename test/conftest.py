import pytest
import os
from pathlib import Path

@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing."""
    env_vars = {
        "HSR_BASE_URL": "https://irs.thsrc.com.tw/IMINT/",
        "START_STATION": "1",
        "END_STATION": "12",
        "TRAVEL_DATE": "2024/03/15",
        "TRAVEL_TIME": "08:00",
        "ADULT_COUNT": "2",
        "CHILD_COUNT": "0",
        "DISABLED_COUNT": "0",
        "ELDER_COUNT": "0",
        "STUDENT_COUNT": "0",
        "PASSENGER_ID": "A123456789",
        "PASSENGER_PHONE": "0912345678",
        "PASSENGER_EMAIL": "test@example.com",
        "HEADLESS": "true",
        "SLOW_MO": "100",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars

@pytest.fixture
def sample_image_bytes():
    """Sample image bytes for captcha testing."""
    # Create a minimal valid PNG image (1x1 pixel)
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )

@pytest.fixture
def temp_image_file(tmp_path, sample_image_bytes):
    """Create a temporary image file for testing."""
    image_path = tmp_path / "test_captcha.png"
    image_path.write_bytes(sample_image_bytes)
    return str(image_path)

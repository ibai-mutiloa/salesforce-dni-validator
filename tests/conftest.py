"""Tests module configuration"""
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


# Set environment variables for testing
os.environ['AZURE_ENDPOINT'] = 'https://test.cognitiveservices.azure.com/'
os.environ['AZURE_API_KEY'] = 'test-key-12345'
os.environ['MIN_NAME_MATCH_SCORE'] = '85.0'


@pytest.fixture
def settings():
    """Get application settings for tests"""
    from app.core.config import get_settings
    # Clear cache to get fresh settings with test env vars
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture
def test_client():
    """Create test client for API"""
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_ocr_data():
    """Create mock OCR data"""
    from app.models import IdDocumentInfo
    return IdDocumentInfo(
        first_name="Jonathan",
        last_name="Garcia",
        document_number="12345678A",
        document_type="DNI",
        date_of_birth="1990-01-15",
        expiration_date="2030-01-15",
        raw_text="Sample document text"
    )

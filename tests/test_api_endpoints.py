"""Unit tests for API endpoints"""
import pytest
import json
from io import BytesIO
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.models import IdDocumentInfo, ValidationStatus


@pytest.fixture
def client(test_client):
    """Get test client"""
    return test_client


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "azure_connected" in data
    
    def test_health_check_response_schema(self, client):
        """Test health check response schema"""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["azure_connected"], bool)


class TestValidateIdentityEndpoint:
    """Tests for identity validation endpoint"""
    
    def test_validate_identity_success(self, client):
        """Test successful identity validation"""
        mock_ocr_data = IdDocumentInfo(
            first_name="Jonathan",
            last_name="Garcia",
            document_number="12345678A",
            document_type="DNI"
        )
        
        # Create a minimal PDF file-like object
        file_content = b"fake pdf content"
        
        with patch('app.core.azure_client.AzureDocumentClient.extract_id_document_info') as mock_extract:
            mock_extract.return_value = mock_ocr_data
            
            response = client.post(
                "/api/v1/validate-identity",
                data={
                    "user_id": "005xx000000xyz",
                    "first_name": "Jonathan",
                    "last_name": "Garcia",
                    "document": ("id_doc.pdf", BytesIO(file_content), "application/pdf")
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OK"
        assert data["confidence_score"] >= 85
        assert data["salesforce_name"] == "Jonathan Garcia"
        assert data["ocr_name"] == "Jonathan Garcia"
        assert data["document_number"] == "12345678A"
    
    def test_validate_identity_mismatch(self, client):
        """Test identity validation with name mismatch"""
        mock_ocr_data = IdDocumentInfo(
            first_name="Carlos",
            last_name="Lopez",
            document_number="87654321B"
        )
        
        file_content = b"fake pdf content"
        
        with patch('app.core.azure_client.AzureDocumentClient.extract_id_document_info') as mock_extract:
            mock_extract.return_value = mock_ocr_data
            
            response = client.post(
                "/api/v1/validate-identity",
                data={
                    "user_id": "005xx000000xyz",
                    "first_name": "Jonathan",
                    "last_name": "Garcia",
                    "document": ("id_doc.pdf", BytesIO(file_content), "application/pdf")
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ERROR"
        assert data["confidence_score"] < 50
        assert data["reason"] is not None
    
    def test_validate_identity_missing_user_id(self, client):
        """Test validation with missing user_id"""
        file_content = b"fake pdf content"
        
        response = client.post(
            "/api/v1/validate-identity",
            data={
                "first_name": "Jonathan",
                "last_name": "Garcia",
                "document": ("id_doc.pdf", BytesIO(file_content), "application/pdf")
            }
        )
        
        # Should fail due to missing required field
        assert response.status_code in [400, 422]
    
    def test_validate_identity_missing_names(self, client):
        """Test validation with missing names"""
        file_content = b"fake pdf content"
        
        response = client.post(
            "/api/v1/validate-identity",
            data={
                "user_id": "005xx000000xyz",
                "document": ("id_doc.pdf", BytesIO(file_content), "application/pdf")
            }
        )
        
        assert response.status_code in [400, 422]
    
    def test_validate_identity_missing_document(self, client):
        """Test validation with missing document"""
        response = client.post(
            "/api/v1/validate-identity",
            data={
                "user_id": "005xx000000xyz",
                "first_name": "Jonathan",
                "last_name": "Garcia"
            }
        )
        
        assert response.status_code in [400, 422]
    
    def test_validate_identity_invalid_file_extension(self, client):
        """Test validation with invalid file extension"""
        file_content = b"fake file content"
        
        response = client.post(
            "/api/v1/validate-identity",
            data={
                "user_id": "005xx000000xyz",
                "first_name": "Jonathan",
                "last_name": "Garcia",
                "document": ("document.txt", BytesIO(file_content), "text/plain")
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid file type" in data.get("detail", "")
    
    def test_validate_identity_valid_file_extensions(self, client):
        """Test validation accepts all valid file extensions"""
        valid_extensions = [
            ("doc.pdf", "application/pdf"),
            ("doc.jpg", "image/jpeg"),
            ("doc.jpeg", "image/jpeg"),
            ("doc.png", "image/png"),
            ("doc.tiff", "image/tiff"),
            ("doc.bmp", "image/bmp")
        ]
        
        for filename, content_type in valid_extensions:
            mock_ocr_data = IdDocumentInfo(
                first_name="Jonathan",
                last_name="Garcia",
                document_number="12345678A"
            )
            
            file_content = b"fake file content"
            
            with patch('app.core.azure_client.AzureDocumentClient.extract_id_document_info') as mock_extract:
                mock_extract.return_value = mock_ocr_data
                
                response = client.post(
                    "/api/v1/validate-identity",
                    data={
                        "user_id": "005xx000000xyz",
                        "first_name": "Jonathan",
                        "last_name": "Garcia",
                        "document": (filename, BytesIO(file_content), content_type)
                    }
                )
            
            assert response.status_code == 200, f"Failed for {filename}"
    
    def test_validate_identity_response_schema(self, client):
        """Test response schema validation"""
        mock_ocr_data = IdDocumentInfo(
            first_name="Jonathan",
            last_name="Garcia",
            document_number="12345678A"
        )
        
        file_content = b"fake pdf content"
        
        with patch('app.core.azure_client.AzureDocumentClient.extract_id_document_info') as mock_extract:
            mock_extract.return_value = mock_ocr_data
            
            response = client.post(
                "/api/v1/validate-identity",
                data={
                    "user_id": "005xx000000xyz",
                    "first_name": "Jonathan",
                    "last_name": "Garcia",
                    "document": ("id_doc.pdf", BytesIO(file_content), "application/pdf")
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = [
            "status", "confidence_score", "salesforce_name", "ocr_name",
            "first_name_score", "last_name_score", "timestamp"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data

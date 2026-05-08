"""Unit tests for validation service"""
import pytest
from app.services.validation_service import IdentityValidationService
from app.models import IdDocumentInfo, ValidationStatus


class TestIdentityValidationService:
    """Tests for identity validation service"""
    
    @pytest.fixture
    def service(self):
        """Create validation service instance"""
        return IdentityValidationService()
    
    def test_exact_match_validation(self, service, mock_ocr_data):
        """Test validation with exact name match"""
        result = service.validate_identity(
            user_id="005xx000000xyz",
            salesforce_first_name="Jonathan",
            salesforce_last_name="Garcia",
            ocr_data=mock_ocr_data
        )
        
        assert result.status == ValidationStatus.OK
        assert result.confidence_score >= 85
        assert result.first_name_score >= 90
        assert result.last_name_score >= 90
        assert result.salesforce_name == "Jonathan Garcia"
        assert result.ocr_name == "Jonathan Garcia"
        assert result.document_number == "12345678A"
    
    def test_similar_match_validation(self, service):
        """Test validation with similar but not exact match"""
        ocr_data = IdDocumentInfo(
            first_name="Jon",
            last_name="Garcia",
            document_number="12345678A"
        )
        
        result = service.validate_identity(
            user_id="005xx000000xyz",
            salesforce_first_name="Jonathan",
            salesforce_last_name="Garcia",
            ocr_data=ocr_data
        )
        
        assert result.status in [ValidationStatus.OK, ValidationStatus.PARTIAL_MATCH]
        assert result.confidence_score > 70
    
    def test_mismatch_validation(self, service):
        """Test validation with mismatched names"""
        ocr_data = IdDocumentInfo(
            first_name="Carlos",
            last_name="Lopez",
            document_number="87654321B"
        )
        
        result = service.validate_identity(
            user_id="005xx000000xyz",
            salesforce_first_name="Jonathan",
            salesforce_last_name="Garcia",
            ocr_data=ocr_data
        )
        
        assert result.status == ValidationStatus.ERROR
        assert result.confidence_score < 50
        assert result.reason is not None
    
    def test_partial_match_validation(self, service):
        """Test validation with partial match"""
        ocr_data = IdDocumentInfo(
            first_name="Jonathan",
            last_name="Lopez",
            document_number="12345678A"
        )
        
        result = service.validate_identity(
            user_id="005xx000000xyz",
            salesforce_first_name="Jonathan",
            salesforce_last_name="Garcia",
            ocr_data=ocr_data
        )
        
        assert result.status == ValidationStatus.PARTIAL_MATCH or result.status == ValidationStatus.ERROR
        assert result.reason is not None
    
    def test_null_ocr_data(self, service):
        """Test validation with null OCR data"""
        result = service.validate_identity(
            user_id="005xx000000xyz",
            salesforce_first_name="Jonathan",
            salesforce_last_name="Garcia",
            ocr_data=None
        )
        
        assert result.status == ValidationStatus.UNKNOWN_DOCUMENT
        assert result.confidence_score == 0.0
        assert result.reason == "No valid data extracted from document"
    
    def test_empty_ocr_names(self, service):
        """Test validation with empty OCR names"""
        ocr_data = IdDocumentInfo(
            first_name="",
            last_name="",
            document_number="12345678A"
        )
        
        result = service.validate_identity(
            user_id="005xx000000xyz",
            salesforce_first_name="Jonathan",
            salesforce_last_name="Garcia",
            ocr_data=ocr_data
        )
        
        assert result.status == ValidationStatus.UNKNOWN_DOCUMENT
        assert result.confidence_score == 0.0
    
    def test_normalized_name_matching(self, service):
        """Test validation with normalized names (accents, case)"""
        ocr_data = IdDocumentInfo(
            first_name="JONATHAN",
            last_name="GARCÍA",
            document_number="12345678A"
        )
        
        result = service.validate_identity(
            user_id="005xx000000xyz",
            salesforce_first_name="jonathan",
            salesforce_last_name="garcia",
            ocr_data=ocr_data
        )
        
        assert result.status == ValidationStatus.OK
        assert result.confidence_score >= 85
    
    def test_whitespace_handling(self, service):
        """Test validation with extra whitespace"""
        ocr_data = IdDocumentInfo(
            first_name="  Jonathan  ",
            last_name="  Garcia  ",
            document_number="12345678A"
        )
        
        result = service.validate_identity(
            user_id="005xx000000xyz",
            salesforce_first_name="  Jonathan  ",
            salesforce_last_name="  Garcia  ",
            ocr_data=ocr_data
        )
        
        assert result.status == ValidationStatus.OK
        assert result.confidence_score >= 85

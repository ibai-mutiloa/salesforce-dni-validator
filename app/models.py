"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ValidationStatus(str, Enum):
    """Validation status enumeration"""
    OK = "OK"
    ERROR = "ERROR"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    UNKNOWN_DOCUMENT = "UNKNOWN_DOCUMENT"


class IdDocumentInfo(BaseModel):
    """Extracted ID document information"""
    first_name: Optional[str] = Field(None, description="First name from document")
    last_name: Optional[str] = Field(None, description="Last name from document")
    document_number: Optional[str] = Field(None, description="Document ID number")
    document_type: Optional[str] = Field(None, description="Type of document (DNI, Passport, etc)")
    date_of_birth: Optional[str] = Field(None, description="Date of birth")
    expiration_date: Optional[str] = Field(None, description="Document expiration date")
    raw_text: Optional[str] = Field(None, description="Raw OCR text for debugging")


class ValidationRequest(BaseModel):
    """Request model for identity validation"""
    user_id: str = Field(..., description="Salesforce User ID")
    first_name: str = Field(..., description="First name from Salesforce", min_length=1)
    last_name: str = Field(..., description="Last name from Salesforce", min_length=1)
    document_file: bytes = Field(..., description="Identity document file (PDF/JPG/PNG)")
    file_name: str = Field(..., description="Original file name with extension")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "005xx000000xyz",
                "first_name": "Jonathan",
                "last_name": "Garcia",
                "document_file": "<binary data>",
                "file_name": "id_document.pdf"
            }
        }


class ValidationResponse(BaseModel):
    """Response model for identity validation"""
    status: ValidationStatus = Field(..., description="Validation result status")
    confidence_score: float = Field(..., ge=0, le=100, description="Fuzzy matching confidence (0-100)")
    salesforce_name: str = Field(..., description="Combined name from Salesforce")
    ocr_name: str = Field(..., description="Combined name from OCR")
    document_number: Optional[str] = Field(None, description="Extracted document number")
    ocr_data: Optional[IdDocumentInfo] = Field(None, description="Full extracted document info")
    reason: Optional[str] = Field(None, description="Mismatch reason or error details")
    first_name_score: float = Field(..., ge=0, le=100, description="First name match score")
    last_name_score: float = Field(..., ge=0, le=100, description="Last name match score")
    timestamp: str = Field(..., description="ISO 8601 timestamp of validation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "OK",
                "confidence_score": 95.5,
                "salesforce_name": "Jonathan Garcia",
                "ocr_name": "Jonathan Garcia",
                "document_number": "12345678A",
                "first_name_score": 100.0,
                "last_name_score": 91.0,
                "reason": None,
                "timestamp": "2026-05-08T10:30:45Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    azure_connected: bool = Field(..., description="Azure service connectivity")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

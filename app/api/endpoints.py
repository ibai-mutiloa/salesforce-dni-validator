"""
API endpoints for identity validation
"""
import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime

from app.models import ValidationResponse, HealthResponse, IdDocumentInfo, ValidationStatus, ErrorResponse
from app.services.validation_service import IdentityValidationService
from app.core.config import get_settings
from app.core.azure_client import get_azure_client

logger = logging.getLogger(__name__)

router = APIRouter()
validation_service = IdentityValidationService()
azure_client = get_azure_client()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        azure_connected=True
    )


@router.post(
    "/validate-identity",
    response_model=ValidationResponse,
    tags=["Validation"],
    summary="Validate Salesforce user against identity document",
    responses={
        200: {
            "description": "Validation completed",
            "model": ValidationResponse
        },
        400: {
            "description": "Invalid request parameters",
            "model": ErrorResponse
        },
        500: {
            "description": "Server error during validation",
            "model": ErrorResponse
        }
    }
)
async def validate_identity(
    user_id: str = Form(..., description="Salesforce User ID"),
    first_name: str = Form(..., description="First name from Salesforce", min_length=1),
    last_name: str = Form(..., description="Last name from Salesforce", min_length=1),
    document: UploadFile = File(..., description="Identity document file (PDF/JPG/PNG)")
):
    """
    Validate Salesforce user registration against identity document.
    
    This endpoint:
    1. Accepts user data and an identity document
    2. Extracts information from the document using Azure Document Intelligence
    3. Compares Salesforce names with extracted names using fuzzy matching
    4. Returns validation status and confidence score
    
    **Request Parameters:**
    - **user_id**: Salesforce User ID (e.g., "005xx000000xyz")
    - **first_name**: User's first name from Salesforce
    - **last_name**: User's last name from Salesforce
    - **document**: Identity document file (PDF, JPG, PNG, etc.)
    
    **Response:**
    - **status**: OK, ERROR, PARTIAL_MATCH, or UNKNOWN_DOCUMENT
    - **confidence_score**: Overall fuzzy match score (0-100)
    - **first_name_score**: First name match score
    - **last_name_score**: Last name match score
    - **reason**: Mismatch details if validation fails
    """
    try:
        # Validate input parameters
        if not user_id or not user_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id cannot be empty"
            )
        
        if not first_name or not first_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="first_name cannot be empty"
            )
        
        if not last_name or not last_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="last_name cannot be empty"
            )
        
        # Validate file
        if not document.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="document filename is required"
            )
        
        # Validate file extension
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        file_extension = '.' + document.filename.lower().split('.')[-1] if '.' in document.filename else ''
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read document file
        file_bytes = await document.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="document file is empty"
            )
        
        logger.info(f"Processing validation request for user {user_id}, document: {document.filename}")
        
        # Extract information from document (synchronous call)
        ocr_data = azure_client.extract_id_document_info(file_bytes, document.filename)
        
        # Validate identity
        validation_result = validation_service.validate_identity(
            user_id=user_id,
            salesforce_first_name=first_name.strip(),
            salesforce_last_name=last_name.strip(),
            ocr_data=ocr_data
        )
        
        logger.info(f"Validation completed for user {user_id}: {validation_result.status}")
        
        return validation_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during validation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during validation"
        )

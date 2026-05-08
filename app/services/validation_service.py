"""
Validation service for comparing Salesforce data with OCR data
"""
import logging
from datetime import datetime
from app.models import ValidationResponse, ValidationStatus, IdDocumentInfo
from app.utils.text_processing import fuzzy_match_names, combine_names
from app.core.config import get_settings


logger = logging.getLogger(__name__)


class IdentityValidationService:
    """Service for validating Salesforce user data against OCR extracted data"""
    
    def __init__(self):
        self.settings = get_settings()
        self.min_match_score = self.settings.MIN_NAME_MATCH_SCORE
    
    def validate_identity(
        self,
        user_id: str,
        salesforce_first_name: str,
        salesforce_last_name: str,
        ocr_data: IdDocumentInfo
    ) -> ValidationResponse:
        """Validate Salesforce user data against OCR extracted data."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Handle case where OCR extraction failed
        if not ocr_data or (not ocr_data.first_name and not ocr_data.last_name):
            logger.warning(f"No valid OCR data extracted for user {user_id}")
            return ValidationResponse(
                status=ValidationStatus.UNKNOWN_DOCUMENT,
                confidence_score=0.0,
                salesforce_name=combine_names(salesforce_first_name, salesforce_last_name),
                ocr_name="",
                document_number=None,
                first_name_score=0.0,
                last_name_score=0.0,
                reason="No valid data extracted from document",
                timestamp=timestamp
            )
        
        # Combine names for comparison
        salesforce_full_name = combine_names(salesforce_first_name, salesforce_last_name)
        ocr_full_name = combine_names(ocr_data.first_name or "", ocr_data.last_name or "")
        
        # Compare first names
        first_name_score, first_match = fuzzy_match_names(
            salesforce_first_name,
            ocr_data.first_name or "",
            self.min_match_score
        )
        
        # Compare last names
        last_name_score, last_match = fuzzy_match_names(
            salesforce_last_name,
            ocr_data.last_name or "",
            self.min_match_score
        )
        
        # Calculate overall confidence score (average of both scores)
        overall_score = (first_name_score + last_name_score) / 2
        
        # Determine validation status
        if first_match and last_match:
            status = ValidationStatus.OK
            reason = None
        elif first_match or last_match:
            status = ValidationStatus.PARTIAL_MATCH
            mismatches = []
            if not first_match:
                mismatches.append(f"First name mismatch (score: {first_name_score:.1f}%)")
            if not last_match:
                mismatches.append(f"Last name mismatch (score: {last_name_score:.1f}%)")
            reason = "; ".join(mismatches)
        else:
            status = ValidationStatus.ERROR
            reason = (
                f"Name mismatch - First name score: {first_name_score:.1f}%, "
                f"Last name score: {last_name_score:.1f}%"
            )
        
        logger.info(
            f"Validation for user {user_id}: status={status}, "
            f"overall_score={overall_score:.1f}%, first_score={first_name_score:.1f}%, "
            f"last_score={last_name_score:.1f}%"
        )
        
        return ValidationResponse(
            status=status,
            confidence_score=overall_score,
            salesforce_name=salesforce_full_name,
            ocr_name=ocr_full_name,
            document_number=ocr_data.document_number,
            ocr_data=ocr_data,
            first_name_score=first_name_score,
            last_name_score=last_name_score,
            reason=reason,
            timestamp=timestamp
        )
        
        salesforce_full_name = combine_names(salesforce_first_name, salesforce_last_name)
        ocr_full_name = combine_names(ocr_data.first_name or "", ocr_data.last_name or "")
        
        logger.info(f"Validating user {user_id}: '{salesforce_full_name}' vs '{ocr_full_name}'")
        
        if not ocr_full_name or not ocr_data.first_name or not ocr_data.last_name:
            logger.warning(f"User {user_id}: Insufficient OCR data extracted")
            return ValidationResponse(
                status=ValidationStatus.UNKNOWN_DOCUMENT,
                confidence_score=0.0,
                salesforce_name=salesforce_full_name,
                ocr_name=ocr_full_name or "[No data extracted]",
                document_number=ocr_data.document_number,
                ocr_data=ocr_data,
                reason="Unable to extract name information from document",
                first_name_score=0.0,
                last_name_score=0.0,
                timestamp=timestamp
            )
        
        first_name_score, first_name_match = fuzzy_match_names(
            salesforce_first_name,
            ocr_data.first_name,
            self.min_match_score
        )
        
        last_name_score, last_name_match = fuzzy_match_names(
            salesforce_last_name,
            ocr_data.last_name,
            self.min_match_score
        )
        
        overall_confidence = (first_name_score + last_name_score) / 2
        
        if first_name_match and last_name_match:
            status = ValidationStatus.OK
            reason = None
            logger.info(f"User {user_id}: VALID - Names match")
        elif first_name_match or last_name_match:
            status = ValidationStatus.PARTIAL_MATCH
            reason = "Partial name match"
            logger.warning(f"User {user_id}: PARTIAL - {reason}")
        else:
            status = ValidationStatus.ERROR
            reason = "Names do not match"
            logger.warning(f"User {user_id}: FAILED - {reason}")
        
        return ValidationResponse(
            status=status,
            confidence_score=round(overall_confidence, 2),
            salesforce_name=salesforce_full_name,
            ocr_name=ocr_full_name,
            document_number=ocr_data.document_number,
            ocr_data=ocr_data,
            reason=reason,
            first_name_score=round(first_name_score, 2),
            last_name_score=round(last_name_score, 2),
            timestamp=timestamp
        )

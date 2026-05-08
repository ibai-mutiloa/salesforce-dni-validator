"""
Azure Document Intelligence client for ID document extraction
"""
import logging
import io
from typing import Optional
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from app.core.config import get_settings
from app.models import IdDocumentInfo

logger = logging.getLogger(__name__)


class AzureDocumentClient:
    """Client for Azure Document Intelligence service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = DocumentIntelligenceClient(
            endpoint=self.settings.AZURE_ENDPOINT,
            credential=AzureKeyCredential(self.settings.AZURE_API_KEY)
        )
    
    def extract_id_document_info(self, file_bytes: bytes, file_name: str) -> Optional[IdDocumentInfo]:
        """
        Extract information from ID document using Azure Document Intelligence.
        
        Args:
            file_bytes: Document file content as bytes
            file_name: Original file name with extension
            
        Returns:
            IdDocumentInfo with extracted data or None if extraction failed
        """
        try:
            logger.info(f"Starting document analysis for {file_name}")
            
            # Determine content type from file extension
            content_type = self._get_content_type(file_name)
            
            # Create request
            request = AnalyzeDocumentRequest(
                base64_source=file_bytes
            )
            
            # Analyze document
            poller = self.client.begin_analyze_document(
                self.settings.AZURE_ANALYZER_ID,
                request
            )
            
            # Wait for completion
            result = poller.result()
            
            logger.info(f"Document analysis completed for {file_name}")
            
            # Extract information from result
            return self._parse_id_document_result(result)
            
        except Exception as e:
            logger.error(f"Error extracting document information: {str(e)}")
            return None
    
    def _get_content_type(self, file_name: str) -> str:
        """Determine content type from file extension."""
        extension = file_name.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'tiff': 'image/tiff',
            'bmp': 'image/bmp'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    def _parse_id_document_result(self, result) -> Optional[IdDocumentInfo]:
        """
        Parse Azure Document Intelligence result and extract ID document information.
        
        Args:
            result: Result from Azure Document Intelligence API
            
        Returns:
            IdDocumentInfo with extracted data
        """
        try:
            if not result.documents or len(result.documents) == 0:
                logger.warning("No documents detected in analysis result")
                return None
            
            document = result.documents[0]
            
            # Extract fields from the document
            fields = document.fields if hasattr(document, 'fields') else {}
            
            # Helper function to safely get field value
            def get_field_value(field_name: str, default=None):
                if field_name in fields:
                    field = fields[field_name]
                    if hasattr(field, 'value'):
                        return field.value
                    elif hasattr(field, 'content'):
                        return field.content
                return default
            
            # Extract common ID document fields
            first_name = get_field_value('FirstName', '')
            last_name = get_field_value('LastName', '')
            document_number = get_field_value('DocumentNumber', '') or get_field_value('DocumentId', '')
            document_type = get_field_value('DocumentType', '')
            date_of_birth = get_field_value('DateOfBirth', '')
            expiration_date = get_field_value('ExpirationDate', '')
            
            # Get raw text content for debugging
            raw_text = document.content if hasattr(document, 'content') else ''
            
            logger.info(
                f"Extracted ID data - Name: {first_name} {last_name}, "
                f"Document: {document_number}, Type: {document_type}"
            )
            
            return IdDocumentInfo(
                first_name=first_name or None,
                last_name=last_name or None,
                document_number=document_number or None,
                document_type=document_type or None,
                date_of_birth=date_of_birth or None,
                expiration_date=expiration_date or None,
                raw_text=raw_text or None
            )
            
        except Exception as e:
            logger.error(f"Error parsing ID document result: {str(e)}")
            return None


def get_azure_client() -> AzureDocumentClient:
    """Get Azure Document Client instance (singleton-like)"""
    return AzureDocumentClient()

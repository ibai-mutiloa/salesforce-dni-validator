"""
Azure Document Intelligence client for ID document extraction
"""
import logging
import re
from typing import Optional
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from app.core.config import get_settings
from app.models import IdDocumentInfo
from app.utils.text_processing import extract_document_number

logger = logging.getLogger(__name__)


class AzureDocumentClient:
    """Client for Azure Document Intelligence service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = DocumentIntelligenceClient(
            endpoint=self.settings.AZURE_ENDPOINT,
            credential=AzureKeyCredential(self.settings.AZURE_API_KEY),
            api_version=self.settings.AZURE_API_VERSION
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
            
            # Create request body from the uploaded document bytes
            request = AnalyzeDocumentRequest(
                bytes_source=file_bytes
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
            raw_text = self._extract_raw_text(result)
            if not raw_text:
                logger.warning("No text content detected in analysis result")
                return None

            # OCR/Read usually returns text paragraphs instead of structured fields.
            # We keep the structured path as a fallback, but prefer the actual OCR text.
            first_name, last_name = self._extract_names_from_text(raw_text)
            document_number = extract_document_number(raw_text)
            document_type = self._extract_document_type(raw_text)
            date_of_birth = self._extract_date_of_birth(raw_text)
            expiration_date = self._extract_expiration_date(raw_text)
            
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

    def _extract_raw_text(self, result) -> str:
        """Build a readable text blob from OCR/Read output."""
        parts = []

        if hasattr(result, "content") and result.content:
            parts.append(str(result.content))

        paragraphs = getattr(result, "paragraphs", None) or []
        for paragraph in paragraphs:
            content = getattr(paragraph, "content", None)
            if content:
                parts.append(str(content))

        documents = getattr(result, "documents", None) or []
        for document in documents:
            content = getattr(document, "content", None)
            if content:
                parts.append(str(content))

        return "\n".join(part.strip() for part in parts if part and part.strip())

    def _extract_names_from_text(self, text: str) -> tuple[str, str]:
        """Extract first and last names from OCR text for Spanish DNI-style documents."""
        lines = [line.strip() for line in re.split(r"[\r\n]+", text) if line.strip()]
        upper_lines = [line.upper() for line in lines]

        first_name = ""
        last_name = ""

        for index, line in enumerate(upper_lines):
            if line.startswith("NOMBRE"):
                candidate = lines[index].split(" ", 1)
                if len(candidate) > 1:
                    first_name = candidate[1].strip()
                elif index + 1 < len(lines):
                    first_name = lines[index + 1].strip()
            elif line.startswith("APELLIDOS"):
                candidate = lines[index].split(" ", 1)
                if len(candidate) > 1:
                    last_name = candidate[1].strip()
                elif index + 1 < len(lines):
                    last_name = lines[index + 1].strip()

        if not first_name and not last_name:
            fallback_names = [line for line in lines if self._looks_like_name_line(line)]
            if fallback_names:
                if len(fallback_names) == 1:
                    first_name = fallback_names[0]
                else:
                    last_name = fallback_names[0]
                    first_name = fallback_names[1]

        return first_name.strip(), last_name.strip()

    def _extract_document_type(self, text: str) -> str:
        """Infer the document type from OCR text."""
        upper_text = text.upper()
        if "DNI" in upper_text:
            return "DNI"
        if "PASAPORTE" in upper_text or "PASSPORT" in upper_text:
            return "Passport"
        return ""

    def _extract_date_of_birth(self, text: str) -> str:
        """Extract a likely birth date from OCR text."""
        match = re.search(r"FECHA\s+DE\s+NACIMIENTO\s*([0-3]?\d[\s/-][0-1]?\d[\s/-]\d{2,4})", text, re.IGNORECASE)
        if match:
            return match.group(1).replace(" ", "/").strip()
        return ""

    def _extract_expiration_date(self, text: str) -> str:
        """Extract a likely expiration date from OCR text."""
        match = re.search(r"VALIDEZ\s*([0-3]?\d[\s/-][0-1]?\d[\s/-]\d{2,4})", text, re.IGNORECASE)
        if match:
            return match.group(1).replace(" ", "/").strip()
        return ""

    def _looks_like_name_line(self, line: str) -> bool:
        """Heuristic to identify a name-like line from OCR output."""
        if not line:
            return False

        if re.search(r"\d", line):
            return False

        normalized = line.upper().strip()
        stopwords = {"ESPANA", "DOCUMENTO", "NACIONAL", "IDENTIDAD", "DNI", "NACIONALIDAD", "FECHA", "NACIMIENTO", "SEXO", "M", "F", "VALIDEZ", "NUM", "SOPORT", "BDA"}
        if normalized in stopwords:
            return False

        words = [word for word in re.split(r"\s+", line) if word]
        return 1 <= len(words) <= 4 and all(word.isalpha() or "-" in word for word in words)


def get_azure_client() -> AzureDocumentClient:
    """Get Azure Document Client instance (singleton-like)"""
    return AzureDocumentClient()

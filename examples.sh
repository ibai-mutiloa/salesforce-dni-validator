#!/bin/bash
# Salesforce Identity Validator - API Examples
# Run these examples against a locally running instance
# Server should be running at http://localhost:8000

BASE_URL="http://localhost:8000"

echo "🔍 Salesforce Identity Validator - API Examples"
echo "================================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Example 1: Health Check
echo -e "${BLUE}1. Health Check${NC}"
echo "URL: GET $BASE_URL/api/v1/health"
echo ""
curl -X GET "$BASE_URL/api/v1/health" -H "Content-Type: application/json"
echo ""
echo ""

# Example 2: Validate Identity - Success Case
echo -e "${BLUE}2. Validate Identity - Matching Names (Success)${NC}"
echo "URL: POST $BASE_URL/api/v1/validate-identity"
echo ""
echo "Creating test document file..."
# Create a simple test file (in production, this would be a real PDF/image)
echo "Sample ID Document" > /tmp/test_doc.txt

echo "Request:"
echo "- user_id: 005xx000000xyz"
echo "- first_name: Jonathan"
echo "- last_name: Garcia"
echo "- document: test document file"
echo ""

curl -X POST "$BASE_URL/api/v1/validate-identity" \
  -F "user_id=005xx000000xyz" \
  -F "first_name=Jonathan" \
  -F "last_name=Garcia" \
  -F "document=@/tmp/test_doc.txt"

echo ""
echo ""

# Example 3: Validate Identity - Mismatched Names
echo -e "${BLUE}3. Validate Identity - Mismatched Names (Error)${NC}"
echo "URL: POST $BASE_URL/api/v1/validate-identity"
echo ""
echo "Request:"
echo "- user_id: 005xx000000abc"
echo "- first_name: Jonathan"
echo "- last_name: Garcia"
echo "- document: test document file"
echo ""

curl -X POST "$BASE_URL/api/v1/validate-identity" \
  -F "user_id=005xx000000abc" \
  -F "first_name=Jonathan" \
  -F "last_name=Garcia" \
  -F "document=@/tmp/test_doc.txt"

echo ""
echo ""

# Example 4: Validate Identity - With Real File
echo -e "${BLUE}4. Validate Identity - With Real PDF File${NC}"
echo "URL: POST $BASE_URL/api/v1/validate-identity"
echo ""
echo "Note: Replace 'sample_document.pdf' with an actual identity document"
echo ""

if [ -f "sample_document.pdf" ]; then
    echo "Found sample_document.pdf, sending request..."
    curl -X POST "$BASE_URL/api/v1/validate-identity" \
      -F "user_id=005xx000000xyz" \
      -F "first_name=Jonathan" \
      -F "last_name=Garcia" \
      -F "document=@sample_document.pdf"
else
    echo "No sample_document.pdf found in current directory"
    echo "To test with real documents, place a PDF in the current directory"
    echo ""
    echo "Example usage:"
    echo "  curl -X POST \"$BASE_URL/api/v1/validate-identity\" \\"
    echo "    -F \"user_id=005xx000000xyz\" \\"
    echo "    -F \"first_name=Jonathan\" \\"
    echo "    -F \"last_name=Garcia\" \\"
    echo "    -F \"document=@/path/to/document.pdf\""
fi

echo ""
echo ""

# Example 5: API Documentation
echo -e "${BLUE}5. Access API Documentation${NC}"
echo ""
echo -e "${GREEN}Swagger UI:${NC} $BASE_URL/docs"
echo -e "${GREEN}ReDoc:${NC} $BASE_URL/redoc"
echo -e "${GREEN}OpenAPI JSON:${NC} $BASE_URL/openapi.json"
echo ""

# Example 6: Invalid Request
echo -e "${BLUE}6. Invalid Request - Missing Required Field${NC}"
echo "URL: POST $BASE_URL/api/v1/validate-identity"
echo ""
echo "This request is missing the 'last_name' field"
echo ""

curl -X POST "$BASE_URL/api/v1/validate-identity" \
  -F "user_id=005xx000000xyz" \
  -F "first_name=Jonathan" \
  -F "document=@/tmp/test_doc.txt"

echo ""
echo ""

# Example 7: Invalid File Type
echo -e "${BLUE}7. Invalid File Type${NC}"
echo "URL: POST $BASE_URL/api/v1/validate-identity"
echo ""
echo "This request uses an invalid file type (.txt instead of .pdf/.jpg/etc)"
echo ""

curl -X POST "$BASE_URL/api/v1/validate-identity" \
  -F "user_id=005xx000000xyz" \
  -F "first_name=Jonathan" \
  -F "last_name=Garcia" \
  -F "document=@/tmp/test_doc.txt;filename=document.txt"

echo ""
echo ""

echo -e "${GREEN}✅ Examples complete!${NC}"
echo ""
echo "For more details, visit:"
echo "- API Docs: http://localhost:8000/docs"
echo "- README: Check README.md file"

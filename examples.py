"""
Salesforce Identity Validator - Python Client Examples

Run this script with a local instance:
    python main.py
    
Then in another terminal:
    python examples.py
"""

import requests
import json
from pathlib import Path
from typing import Dict, Any


class IdentityValidatorClient:
    """Simple client for Identity Validator API"""
    
    def __init__(self, base_url: str = "http://localhost:5003"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()
        return response.json()
    
    def validate_identity(
        self,
        user_id: str,
        first_name: str,
        last_name: str,
        document_path: str
    ) -> Dict[str, Any]:
        """Validate user identity against document"""
        
        with open(document_path, "rb") as f:
            files = {"document": f}
            data = {
                "user_id": user_id,
                "first_name": first_name,
                "last_name": last_name
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/validate-identity",
                files=files,
                data=data
            )
        
        response.raise_for_status()
        return response.json()
    
    def print_validation_result(self, result: Dict[str, Any]) -> None:
        """Pretty print validation result"""
        print("\n" + "="*60)
        print("VALIDATION RESULT")
        print("="*60)
        
        print(f"\nStatus: {result['status']}")
        print(f"Confidence Score: {result['confidence_score']:.1f}%")
        print(f"First Name Score: {result['first_name_score']:.1f}%")
        print(f"Last Name Score: {result['last_name_score']:.1f}%")
        print(f"\nSalesforce Name: {result['salesforce_name']}")
        print(f"OCR Name: {result['ocr_name']}")
        print(f"Document Number: {result['document_number']}")
        
        if result['reason']:
            print(f"Reason: {result['reason']}")
        
        print(f"Timestamp: {result['timestamp']}")
        
        if result['ocr_data']:
            print("\nExtracted Document Data:")
            ocr = result['ocr_data']
            if ocr.get('first_name'):
                print(f"  First Name: {ocr['first_name']}")
            if ocr.get('last_name'):
                print(f"  Last Name: {ocr['last_name']}")
            if ocr.get('document_number'):
                print(f"  Document Number: {ocr['document_number']}")
            if ocr.get('document_type'):
                print(f"  Document Type: {ocr['document_type']}")
            if ocr.get('date_of_birth'):
                print(f"  Date of Birth: {ocr['date_of_birth']}")
            if ocr.get('expiration_date'):
                print(f"  Expiration Date: {ocr['expiration_date']}")
        
        print("="*60 + "\n")


def create_test_file(path: str) -> None:
    """Create a test file for demonstration"""
    with open(path, "w") as f:
        f.write("Test Identity Document\n")
        f.write("This is a sample document for API testing\n")


def main():
    """Run examples"""
    
    print("\n")
    print("█" * 60)
    print("█  Salesforce Identity Validator - Python Examples")
    print("█" * 60)
    print()
    
    # Initialize client
    client = IdentityValidatorClient()
    
    # Example 1: Health Check
    print("\n" + "▶" * 30)
    print("Example 1: Health Check")
    print("▶" * 30)
    
    try:
        health = client.health_check()
        print(f"✓ Health Status: {health['status']}")
        print(f"✓ Version: {health['version']}")
        print(f"✓ Azure Connected: {health['azure_connected']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Make sure the API is running: python main.py")
        return
    
    # Example 2: Validate Identity with Exact Match
    print("\n" + "▶" * 30)
    print("Example 2: Validate Identity (Exact Match)")
    print("▶" * 30)
    
    try:
        # Create test file
        test_file = "/tmp/test_document.txt"
        create_test_file(test_file)
        
        print("Request:")
        print("  user_id: 005xx000000xyz")
        print("  first_name: Jonathan")
        print("  last_name: Garcia")
        print("  document: test_document.txt")
        
        result = client.validate_identity(
            user_id="005xx000000xyz",
            first_name="Jonathan",
            last_name="Garcia",
            document_path=test_file
        )
        
        client.print_validation_result(result)
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Request Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 3: Validate Identity with Similar Names
    print("\n" + "▶" * 30)
    print("Example 3: Validate Identity (Similar Names)")
    print("▶" * 30)
    
    try:
        print("Request:")
        print("  user_id: 005xx000000abc")
        print("  first_name: Jon")  # Similar to Jonathan
        print("  last_name: Garcia")
        print("  document: test_document.txt")
        
        result = client.validate_identity(
            user_id="005xx000000abc",
            first_name="Jon",
            last_name="Garcia",
            document_path=test_file
        )
        
        client.print_validation_result(result)
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Request Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 4: Validate Identity with Mismatched Names
    print("\n" + "▶" * 30)
    print("Example 4: Validate Identity (Mismatched Names)")
    print("▶" * 30)
    
    try:
        print("Request:")
        print("  user_id: 005xx000000def")
        print("  first_name: Carlos")
        print("  last_name: Lopez")
        print("  document: test_document.txt")
        
        result = client.validate_identity(
            user_id="005xx000000def",
            first_name="Carlos",
            last_name="Lopez",
            document_path=test_file
        )
        
        client.print_validation_result(result)
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Request Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 5: Error Handling - Missing field
    print("\n" + "▶" * 30)
    print("Example 5: Error Handling - Validation Errors")
    print("▶" * 30)
    
    try:
        print("Request:")
        print("  user_id: 005xx000000xyz")
        print("  first_name: Jonathan")
        print("  last_name: (missing)")
        print("  document: test_document.txt")
        
        # Attempt with missing last_name
        response = requests.post(
            "http://localhost:5003/api/v1/validate-identity",
            data={
                "user_id": "005xx000000xyz",
                "first_name": "Jonathan"
                # last_name is missing
            },
            files={"document": open(test_file, "rb")}
        )
        
        if response.status_code != 200:
            print(f"✓ Validation Error Caught (Status: {response.status_code})")
            error_detail = response.json()
            print(f"  Error: {error_detail.get('detail', 'Unknown error')}")
        
    except Exception as e:
        print(f"✓ Expected Error Caught: {type(e).__name__}")
    
    # Example 6: Processing with Custom Parameters
    print("\n" + "▶" * 30)
    print("Example 6: API Response Format")
    print("▶" * 30)
    
    try:
        result = client.validate_identity(
            user_id="005xx000000xyz",
            first_name="Jonathan",
            last_name="Garcia",
            document_path=test_file
        )
        
        print("\nFull JSON Response:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 7: Batch Processing
    print("\n" + "▶" * 30)
    print("Example 7: Batch Processing (Multiple Users)")
    print("▶" * 30)
    
    batch_users = [
        ("005xx000000xyz", "Jonathan", "Garcia"),
        ("005xx000000abc", "Maria", "Rodriguez"),
        ("005xx000000def", "Carlos", "Lopez"),
    ]
    
    results = []
    for user_id, first_name, last_name in batch_users:
        try:
            print(f"\nProcessing: {first_name} {last_name}...")
            result = client.validate_identity(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                document_path=test_file
            )
            results.append({
                'user_id': user_id,
                'name': f"{first_name} {last_name}",
                'status': result['status'],
                'score': result['confidence_score']
            })
            print(f"  Status: {result['status']} ({result['confidence_score']:.1f}%)")
        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                'user_id': user_id,
                'name': f"{first_name} {last_name}",
                'status': 'ERROR',
                'score': 0
            })
    
    print("\n" + "═" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("═" * 60)
    
    for result in results:
        status_symbol = "✓" if result['status'] == 'OK' else "✗"
        print(f"{status_symbol} {result['name']:20} | {result['status']:15} | {result['score']:.1f}%")
    
    print("=" * 60)
    
    # Summary
    print("\n" + "▶" * 30)
    print("Examples Complete!")
    print("▶" * 30)
    
    print("\nTo continue working with the API:")
    print("  1. Access Swagger UI: http://localhost:5003/docs")
    print("  2. Read README.md for detailed documentation")
    print("  3. Check app/api/endpoints.py for implementation details")
    print("  4. Run tests: pytest -v")
    print()


if __name__ == "__main__":
    main()

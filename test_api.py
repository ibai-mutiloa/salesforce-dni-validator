"""Example validation requests for testing the API"""
import requests
import json
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:5003/api/v1"
FIXTURE_PATH = Path("tests/fixtures/dni.jpg")


def test_health_check():
    """Test health check endpoint"""
    print("\n=== Health Check ===")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_validation():
    """Test validation endpoint"""
    print("\n=== Validation Test ===")
    
    data = {
        "user_id": "005xx000000xyz",
        "first_name": "Jonathan",
        "last_name": "Garcia"
    }
    
    if not FIXTURE_PATH.exists():
        print(f"Error: Fixture not found at {FIXTURE_PATH}")
        return

    with FIXTURE_PATH.open("rb") as document_file:
        files = {"document": (FIXTURE_PATH.name, document_file, "image/jpeg")}
        response = requests.post(f"{API_BASE_URL}/validate-identity", files=files, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    try:
        test_health_check()
        test_validation()
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to {API_BASE_URL}")
        print("Make sure the API is running (python main.py)")

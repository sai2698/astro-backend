import sys
import os

# Add the backend dir to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing /api/v1/courses...")
response = client.get("/api/v1/courses/")
print("Status Code:", response.status_code)
try:
    print("Response:", response.json())
except Exception as e:
    print("Error parsing json:", e)

print("\nTesting /api/v1/categories...")
response = client.get("/api/v1/categories/")
print("Status Code:", response.status_code)
try:
    print("Response:", response.json())
except Exception as e:
    print("Error parsing json:", e)

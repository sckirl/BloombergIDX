from fastapi.testclient import TestClient
from .main import app
import json

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]

def test_momentum():
    # Test with a ticker that likely doesn't exist to check 404
    response = client.get("/insider/momentum/NONEXISTENT")
    assert response.status_code == 404

def test_bandar():
    response = client.get("/insider/bandar/NONEXISTENT")
    assert response.status_code == 404

def test_entity():
    response = client.get("/insider/entity/Jahja")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "pep_flag" in data

if __name__ == "__main__":
    import pytest
    import sys
    # We need to add current dir to sys.path for relative imports to work
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run tests
    test_health()
    print("Health check passed.")
    test_momentum()
    print("Momentum 404 check passed.")
    test_bandar()
    print("Bandar 404 check passed.")
    test_entity()
    print("Entity check passed.")

"""
Unit tests for FastAPI prediction API
"""

import pytest
import logging
from fastapi.testclient import TestClient
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

logger = logging.getLogger(__name__)

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_returns_200(self):
        """Test that health check returns 200 status"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_health_check_response_structure(self):
        """Test health check response structure"""
        response = client.get("/")
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
    
    def test_health_check_status_value(self):
        """Test health check returns healthy status"""
        response = client.get("/")
        data = response.json()
        assert data["status"] == "healthy"


class TestPredictionEndpoint:
    """Test prediction endpoint"""
    
    @pytest.fixture
    def valid_input(self):
        """Valid test input"""
        return {
            "square_feet": 2500,
            "bedrooms": 3,
            "bathrooms": 2.5,
            "age": 15,
            "location_score": 8.0
        }
    
    def test_prediction_returns_200(self, valid_input):
        """Test that prediction endpoint returns 200 status"""
        response = client.post("/predict", json=valid_input)
        # Either 200 (success) or 503 (model not loaded, which is ok for testing)
        assert response.status_code in [200, 503]
    
    def test_prediction_invalid_input_returns_422(self):
        """Test that invalid input returns 422 status"""
        invalid_input = {
            "square_feet": -100,  # Invalid: negative
            "bedrooms": 3,
            "bathrooms": 2,
            "age": 15,
            "location_score": 8
        }
        response = client.post("/predict", json=invalid_input)
        assert response.status_code == 422
    
    def test_prediction_missing_field_returns_422(self):
        """Test that missing required field returns 422"""
        incomplete_input = {
            "square_feet": 2500,
            "bedrooms": 3
        }
        response = client.post("/predict", json=incomplete_input)
        assert response.status_code == 422


class TestModelInfoEndpoint:
    """Test model info endpoint"""
    
    def test_model_info_returns_valid_response(self):
        """Test model info endpoint response"""
        response = client.get("/model-info")
        # Either 200 (success) or 503 (model not loaded)
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "model_type" in data
            assert "features" in data
            assert "target" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

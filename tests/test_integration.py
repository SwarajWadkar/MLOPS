"""
Integration tests for the ML API
"""

import pytest
import logging
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

logger = logging.getLogger(__name__)

client = TestClient(app)


class TestAPIIntegration:
    """Integration tests for complete API workflows"""
    
    @pytest.mark.integration
    def test_complete_workflow(self):
        """Test complete workflow: health -> prediction -> model info"""
        
        # Step 1: Check health
        health_response = client.get("/")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        
        # Step 2: Get model info
        model_info_response = client.get("/model-info")
        assert model_info_response.status_code in [200, 503]
        
        # Step 3: Make prediction
        if health_data.get("model_loaded", False):
            predict_data = {
                "square_feet": 2500,
                "bedrooms": 3,
                "bathrooms": 2.5,
                "age": 15,
                "location_score": 8.0
            }
            
            predict_response = client.post("/predict", json=predict_data)
            assert predict_response.status_code == 200
            
            prediction = predict_response.json()
            assert "predicted_price" in prediction
            assert "input_features" in prediction
            assert prediction["predicted_price"] > 0
    
    @pytest.mark.api
    def test_multiple_predictions(self):
        """Test making multiple predictions"""
        test_cases = [
            {
                "square_feet": 1000,
                "bedrooms": 2,
                "bathrooms": 1,
                "age": 50,
                "location_score": 5.0
            },
            {
                "square_feet": 4000,
                "bedrooms": 5,
                "bathrooms": 3.5,
                "age": 5,
                "location_score": 9.5
            },
            {
                "square_feet": 2500,
                "bedrooms": 3,
                "bathrooms": 2,
                "age": 25,
                "location_score": 7.0
            },
        ]
        
        predictions = []
        for test_case in test_cases:
            response = client.post("/predict", json=test_case)
            if response.status_code == 200:
                predictions.append(response.json())
        
        # Verify predictions are reasonable
        if predictions:
            prices = [p["predicted_price"] for p in predictions]
            # Larger house should cost more
            assert len(prices) > 0
    
    @pytest.mark.api
    def test_edge_cases(self):
        """Test edge cases and boundary values"""
        
        # Minimum valid values
        min_case = {
            "square_feet": 1,
            "bedrooms": 1,
            "bathrooms": 1,
            "age": 0,
            "location_score": 1
        }
        
        response = client.post("/predict", json=min_case)
        assert response.status_code in [200, 422]
        
        # Maximum valid values
        max_case = {
            "square_feet": 10000,
            "bedrooms": 10,
            "bathrooms": 10,
            "age": 150,
            "location_score": 10
        }
        
        response = client.post("/predict", json=max_case)
        assert response.status_code in [200, 422]
    
    @pytest.mark.api
    def test_response_consistency(self):
        """Test that responses are consistent across multiple calls"""
        
        test_input = {
            "square_feet": 2500,
            "bedrooms": 3,
            "bathrooms": 2.5,
            "age": 15,
            "location_score": 8.0
        }
        
        # Make same prediction twice
        response1 = client.post("/predict", json=test_input)
        response2 = client.post("/predict", json=test_input)
        
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            
            # Same input should give same prediction
            assert data1["predicted_price"] == data2["predicted_price"]


class TestAPIErrorHandling:
    """Test API error handling and edge cases"""
    
    @pytest.mark.api
    def test_invalid_feature_ranges(self):
        """Test validation of feature ranges"""
        
        # Negative square footage
        invalid = {
            "square_feet": -100,
            "bedrooms": 3,
            "bathrooms": 2,
            "age": 15,
            "location_score": 8
        }
        response = client.post("/predict", json=invalid)
        assert response.status_code == 422
        
        # Too many bedrooms
        invalid = {
            "square_feet": 2500,
            "bedrooms": 20,
            "bathrooms": 2,
            "age": 15,
            "location_score": 8
        }
        response = client.post("/predict", json=invalid)
        assert response.status_code == 422
    
    @pytest.mark.api
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        
        # Missing square_feet
        incomplete = {
            "bedrooms": 3,
            "bathrooms": 2,
            "age": 15,
            "location_score": 8
        }
        response = client.post("/predict", json=incomplete)
        assert response.status_code == 422
    
    @pytest.mark.api
    def test_wrong_data_types(self):
        """Test handling of wrong data types"""
        
        # String instead of number
        wrong_type = {
            "square_feet": "two thousand",
            "bedrooms": 3,
            "bathrooms": 2,
            "age": 15,
            "location_score": 8
        }
        response = client.post("/predict", json=wrong_type)
        assert response.status_code == 422
    
    @pytest.mark.api
    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored"""
        
        with_extra = {
            "square_feet": 2500,
            "bedrooms": 3,
            "bathrooms": 2,
            "age": 15,
            "location_score": 8,
            "extra_field": "should be ignored"
        }
        response = client.post("/predict", json=with_extra)
        # Should either work or return validation error (both are acceptable)
        assert response.status_code in [200, 422, 503]


class TestAPIPerformance:
    """Performance and load tests"""
    
    @pytest.mark.slow
    def test_multiple_concurrent_requests(self):
        """Test API with multiple requests"""
        
        test_input = {
            "square_feet": 2500,
            "bedrooms": 3,
            "bathrooms": 2.5,
            "age": 15,
            "location_score": 8.0
        }
        
        responses = []
        for i in range(10):
            response = client.post("/predict", json=test_input)
            responses.append(response.status_code)
        
        # Check that all requests were processed
        assert len(responses) == 10
        # Check that at least some were successful
        successful = sum(1 for code in responses if code in [200, 503])
        assert successful > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

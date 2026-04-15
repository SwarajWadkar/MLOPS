"""
Pytest configuration and fixtures
"""

import pytest
import sys
import os
import joblib
import logging
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np


# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import main as app_module

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment and ensure model is loaded/created"""
    os.environ['API_DEBUG'] = 'False'
    
    # Ensure model directory exists
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'model')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'model.pkl')
    scaler_path = os.path.join(model_dir, 'scaler.pkl')
    
    # If model files don't exist, create dummy ones for testing
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        logger.warning("Model files not found. Creating dummy model for testing...")
        
        # Create dummy model
        model = LinearRegression()
        X_dummy = np.array([
            [2500, 3, 2.5, 15, 8],
            [3000, 4, 3, 20, 7],
            [2000, 2, 1.5, 10, 9],
        ])
        y_dummy = np.array([800000, 950000, 700000])
        
        model.fit(X_dummy, y_dummy)
        
        # Create dummy scaler
        scaler = StandardScaler()
        scaler.fit(X_dummy)
        
        # Save dummy model and scaler
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        logger.warning(f"Created dummy model at {model_path}")
        logger.warning(f"Created dummy scaler at {scaler_path}")
    
    # Load model into app
    app_module.load_model()
    logger.info(f"Model loaded for testing: {app_module.model is not None}")
    logger.info(f"Scaler loaded for testing: {app_module.scaler is not None}")
    
    yield


@pytest.fixture
def sample_features():
    """Sample valid input features for testing"""
    return {
        "square_feet": 2500,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "age": 15,
        "location_score": 8.0
    }


@pytest.fixture
def invalid_features():
    """Invalid input features for testing"""
    return {
        "square_feet": -100,
        "bedrooms": 15,
        "bathrooms": -2,
        "age": 200,
        "location_score": 15
    }

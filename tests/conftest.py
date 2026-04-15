"""
Pytest configuration and fixtures
"""

import pytest
import sys
import os


# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment once for all tests"""
    os.environ['API_DEBUG'] = 'False'
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

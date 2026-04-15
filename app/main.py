"""
FastAPI Application for ML Model Prediction
Provides endpoints for health check and price prediction
"""

import logging
import os
import joblib
import numpy as np
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')

# Global variables to hold model and scaler
model = None
scaler = None


def load_model():
    """
    Load trained model and scaler from disk
    """
    global model, scaler
    
    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}")
        
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        logger.info("✓ Model and scaler loaded successfully")
        logger.info(f"  Model type: {type(model).__name__}")
        logger.info(f"  Scaler type: {type(scaler).__name__}")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return False


# Initialize FastAPI app
app = FastAPI(
    title="ML Housing Price Prediction API",
    description="API for predicting house prices using scikit-learn model",
    version="1.0.0"
)


# Startup event - load model when app starts
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler - load model and scaler
    """
    logger.info("Starting up ML Prediction API...")
    logger.info(f"Looking for model at: {MODEL_PATH}")
    logger.info(f"Looking for scaler at: {SCALER_PATH}")
    
    if load_model():
        logger.info("✓ Model initialization successful")
    else:
        logger.error("✗ Model initialization failed - API will return 503 for predictions")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    """
    logger.info("Shutting down ML Prediction API...")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class HouseFeatures(BaseModel):
    """Input features for prediction"""
    square_feet: float = Field(..., gt=0, description="Square footage of the house")
    bedrooms: int = Field(..., ge=1, le=10, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=1, le=10, description="Number of bathrooms")
    age: int = Field(..., ge=0, le=150, description="Age of the house in years")
    location_score: float = Field(..., ge=1, le=10, description="Location score (1-10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "square_feet": 2500,
                "bedrooms": 3,
                "bathrooms": 2,
                "age": 15,
                "location_score": 8
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response"""
    predicted_price: float = Field(..., description="Predicted house price")
    input_features: dict = Field(..., description="Input features used for prediction")
    model_version: str = Field(..., description="Model version")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status")
    model_loaded: bool = Field(..., description="Whether model is loaded")


# API Endpoints

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "model_loaded": model is not None and scaler is not None
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(features: HouseFeatures):
    """
    Make a price prediction based on house features
    
    Args:
        features: HouseFeatures object with property details
        
    Returns:
        PredictionResponse with predicted price
    """
    # Check if model is loaded FIRST
    if model is None or scaler is None:
        logger.error("Model or scaler not loaded - cannot make prediction")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please try again later."
        )
    
    try:
        logger.info(f"Prediction request received: {features}")
        
        # Prepare input features as numpy array
        input_array = np.array([[
            features.square_feet,
            features.bedrooms,
            features.bathrooms,
            features.age,
            features.location_score
        ]])
        
        # Scale features using loaded scaler
        scaled_features = scaler.transform(input_array)
        
        # Make prediction using loaded model
        prediction = model.predict(scaled_features)
        predicted_price = float(prediction[0])
        
        logger.info(f"Prediction made: ${predicted_price:,.2f}")
        
        # Return response as dict (NOT callable)
        response = {
            "predicted_price": predicted_price,
            "input_features": features.dict(),
            "model_version": "1.0.0"
        }
        return response
        
    except ValueError as e:
        logger.error(f"Feature validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input features: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during prediction. Please check logs."
        )


@app.get("/model-info", tags=["Model"])
async def model_info():
    """
    Get information about the loaded model
    Returns model metadata and status
    """
    if model is None or scaler is None:
        logger.error("Model info requested but model not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please try again later."
        )
    
    # Return model information as dict
    info_response = {
        "model_type": "LinearRegression",
        "model_version": "1.0.0",
        "features": [
            "square_feet",
            "bedrooms",
            "bathrooms",
            "age",
            "location_score"
        ],
        "target": "price",
        "status": "loaded"
    }
    return info_response


# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler with logging"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

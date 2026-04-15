"""
Machine Learning Model Training Script
Trains a housing price prediction model using scikit-learn
"""

import logging
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create model directory if it doesn't exist
MODEL_DIR = os.path.join(os.path.dirname(__file__))
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')


def create_synthetic_data(n_samples=200):
    """
    Create synthetic housing dataset for demonstration
    Features: square_feet, bedrooms, bathrooms, age, location_score
    Target: price
    """
    logger.info(f"Creating synthetic dataset with {n_samples} samples")
    
    np.random.seed(42)
    
    square_feet = np.random.uniform(800, 5000, n_samples)
    bedrooms = np.random.randint(1, 6, n_samples)
    bathrooms = np.random.uniform(1, 4, n_samples)
    age = np.random.randint(1, 100, n_samples)
    location_score = np.random.uniform(1, 10, n_samples)
    
    # Generate price based on features (with some noise)
    price = (
        150 * square_feet +
        30000 * bedrooms +
        25000 * bathrooms -
        500 * age +
        50000 * location_score +
        np.random.normal(0, 50000, n_samples)
    )
    
    data = pd.DataFrame({
        'square_feet': square_feet,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'age': age,
        'location_score': location_score,
        'price': price
    })
    
    logger.info(f"Dataset created with shape: {data.shape}")
    logger.info(f"\nDataset preview:\n{data.head()}")
    
    return data


def preprocess_data(X):
    """
    Preprocess features: handle missing values and scale
    """
    logger.info("Preprocessing data...")
    
    # Handle missing values (fill with mean)
    X_filled = X.fillna(X.mean())
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_filled)
    
    logger.info(f"Data preprocessing complete. Shape: {X_scaled.shape}")
    
    return X_scaled, scaler


def train_model(X_train, y_train):
    """
    Train Linear Regression model
    """
    logger.info("Training Linear Regression model...")
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    logger.info("Model training complete")
    logger.info(f"Model coefficients: {model.coef_}")
    logger.info(f"Model intercept: {model.intercept_}")
    
    return model


def evaluate_model(model, X_test, y_test, set_name="Test"):
    """
    Evaluate model performance
    """
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"\n{set_name} Set Metrics:")
    logger.info(f"  RMSE: ${rmse:,.2f}")
    logger.info(f"  MAE: ${mae:,.2f}")
    logger.info(f"  R² Score: {r2:.4f}")
    
    return {'rmse': rmse, 'mae': mae, 'r2': r2, 'mse': mse}


def save_model(model, scaler):
    """
    Save model and scaler using joblib
    """
    logger.info(f"Saving model to {MODEL_PATH}")
    joblib.dump(model, MODEL_PATH)
    
    logger.info(f"Saving scaler to {SCALER_PATH}")
    joblib.dump(scaler, SCALER_PATH)
    
    logger.info("Model and scaler saved successfully")


def main():
    """
    Main training pipeline
    """
    logger.info("=" * 60)
    logger.info("Machine Learning Model Training Pipeline")
    logger.info("=" * 60)
    
    try:
        # Step 1: Load/Create data
        data = create_synthetic_data(n_samples=200)
        
        # Step 2: Separate features and target
        X = data.drop('price', axis=1)
        y = data['price']
        
        logger.info(f"\nFeatures shape: {X.shape}")
        logger.info(f"Target shape: {y.shape}")
        
        # Step 3: Split data
        logger.info("\nSplitting data into train (80%) and test (20%) sets...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        logger.info(f"Training set size: {X_train.shape[0]}")
        logger.info(f"Test set size: {X_test.shape[0]}")
        
        # Step 4: Preprocess
        X_train_scaled, scaler = preprocess_data(X_train)
        X_test_scaled, _ = preprocess_data(X_test)
        
        # Step 5: Train model
        model = train_model(X_train_scaled, y_train)
        
        # Step 6: Evaluate
        logger.info("\n" + "=" * 60)
        train_metrics = evaluate_model(model, X_train_scaled, y_train, "Training")
        test_metrics = evaluate_model(model, X_test_scaled, y_test, "Test")
        logger.info("=" * 60)
        
        # Step 7: Save model
        save_model(model, scaler)
        
        logger.info("\n✓ Training pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

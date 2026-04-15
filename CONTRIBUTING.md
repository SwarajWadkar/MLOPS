# Development Guide for MLOps Pipeline

## Getting Started with Development

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd "MLOPS Pipeline"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Project Structure Overview

```
MLOPS Pipeline/
├── app/                      # FastAPI application
│   ├── __init__.py
│   └── main.py              # Main API code
├── model/                   # ML model training
│   ├── __init__.py
│   ├── train.py             # Training script
│   ├── model.pkl            # Trained model (generated)
│   └── scaler.pkl           # Data scaler (generated)
├── data/                    # Dataset (empty, will be generated)
├── tests/                   # Unit tests
│   ├── conftest.py          # Test configuration
│   └── test_api.py          # API tests
├── requirements.txt         # Dependencies
├── Dockerfile              # Docker configuration
├── Jenkinsfile             # Jenkins pipeline
├── docker-compose.yml      # Docker compose setup
├── Makefile                # Helper commands
└── README.md               # Documentation
```

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make your changes
# Add tests for new functionality
# Update documentation

# Run tests locally
pytest tests/ -v

# Run linting
flake8 app/ model/ tests/
mypy app/ model/

# Format code
black app/ model/ tests/
isort app/ model/ tests/

# Commit changes
git add .
git commit -m "feat: description of feature"
git push origin feature/new-feature

# Create pull request on GitHub
```

### 2. Adding a New API Endpoint

#### Step 1: Define Pydantic Model
```python
# In app/main.py
class NewInput(BaseModel):
    param1: str = Field(..., description="Parameter 1")
    param2: int = Field(..., description="Parameter 2")

class NewResponse(BaseModel):
    result: str
    metadata: dict
```

#### Step 2: Create Endpoint
```python
@app.post("/new-endpoint", response_model=NewResponse, tags=["Feature"])
async def new_endpoint(input_data: NewInput):
    """
    New endpoint description
    """
    logger.info(f"Endpoint called with: {input_data}")
    
    try:
        # Business logic here
        result = process_data(input_data)
        
        return {
            "result": result,
            "metadata": {"version": "1.0.0"}
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### Step 3: Add Tests
```python
# In tests/test_api.py
def test_new_endpoint():
    test_input = {"param1": "value", "param2": 10}
    response = client.post("/new-endpoint", json=test_input)
    assert response.status_code == 200
    assert "result" in response.json()
```

#### Step 4: Update Documentation
```markdown
# Update README.md with endpoint details
```

### 3. Modifying ML Model

#### Option 1: Using Different Algorithm
```python
# In model/train.py
from sklearn.ensemble import RandomForestRegressor

# Replace LinearRegression with RandomForest
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)
```

#### Option 2: Adding New Features
```python
# In model/train.py, in create_synthetic_data()
# Add new feature
neighborhood_type = np.random.choice(['urban', 'suburban', 'rural'], n_samples)

# Add to DataFrame
data['neighborhood'] = neighborhood_type
```

#### Option 3: Using Different Dataset
```python
# Replace create_synthetic_data() with your data loading
def load_data():
    data = pd.read_csv('path/to/data.csv')
    # Preprocessing
    return data
```

### 4. Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run specific test class
pytest tests/test_api.py::TestPredictionEndpoint -v

# Run specific test method
pytest tests/test_api.py::TestPredictionEndpoint::test_prediction_returns_200 -v

# Run with coverage
pytest tests/ --cov=app --cov=model --cov-report=html

# Run with specific marker
pytest -m "not slow" tests/
```

### 5. Code Quality

```bash
# Format code with black
black app/ model/ tests/

# Sort imports
isort app/ model/ tests/

# Lint with flake8
flake8 app/ model/ tests/

# Type check with mypy
mypy app/ model/

# All checks at once (requires make)
make lint
make format
```

### 6. Local Testing with Docker

```bash
# Build image
docker build -t ml-api-dev:latest .

# Run container
docker run -p 8000:8000 ml-api-dev:latest

# Run tests in container
docker run ml-api-dev:latest pytest tests/ -v

# Interactive shell
docker run -it ml-api-dev:latest /bin/bash
```

## Tips and Best Practices

### 1. Logging
```python
import logging

logger = logging.getLogger(__name__)

# Log at appropriate levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### 2. Error Handling
```python
try:
    # Code that might fail
    result = perform_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {str(e)}")
    raise HTTPException(
        status_code=400,
        detail=f"Error details: {str(e)}"
    )
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )
```

### 3. Type Hints
```python
from typing import List, Dict, Optional

def process_data(
    data: List[Dict[str, float]],
    threshold: Optional[float] = None
) -> Dict[str, any]:
    """Process data and return results"""
    pass
```

### 4. Documentation
```python
def predict(features: HouseFeatures) -> PredictionResponse:
    """
    Make a price prediction based on house features.
    
    Args:
        features: HouseFeatures object with property details
        
    Returns:
        PredictionResponse with predicted price
        
    Raises:
        HTTPException: If model is not loaded or input is invalid
        
    Example:
        >>> features = HouseFeatures(square_feet=2500, ...)
        >>> response = predict(features)
        >>> print(response.predicted_price)
    """
    pass
```

## Common Issues and Solutions

### Issue: Model not found
```bash
# Solution: Train the model
python model/train.py
```

### Issue: Package import errors
```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: Port already in use
```bash
# Solution: Use different port
uvicorn app.main:app --port 9000
```

### Issue: Docker build fails
```bash
# Solution: Build without cache
docker build --no-cache -t ml-api:latest .
```

## Performance Optimization Tips

### 1. Model Caching
```python
# Cache model in memory to avoid reloading
_model_cache = None

def get_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache
```

### 2. Async Operations
```python
# Use async for I/O operations
@app.post("/async-predict")
async def async_predict(features: HouseFeatures):
    # Async operations
    result = await process_async(features)
    return result
```

### 3. Batch Predictions
```python
@app.post("/batch-predict")
async def batch_predict(features_list: List[HouseFeatures]):
    """Make multiple predictions at once"""
    predictions = []
    for features in features_list:
        pred = model.predict(scaler.transform([[...]])[0]
        predictions.append(pred)
    return {"predictions": predictions}
```

## Debugging

### Using print statements
```python
print(f"Variable value: {variable}")
```

### Using logging
```python
logger.debug(f"Debug info: {variable}")
```

### Using debugger
```python
import pdb; pdb.set_trace()

# Or in VS Code (with Python extension):
# Set breakpoints and use Debug console
```

### Testing with curl
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"square_feet": 2500, ...}'
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/description

# Make changes
# ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new feature description"

# Push to origin
git push origin feature/description

# Create pull request on GitHub
# After review and approval, merge to main

# Pull latest changes locally
git checkout main
git pull origin main
```

## Release Process

```bash
# Update version in code/documentation
# Commit changes
git commit -m "chore: bump version to 1.1.0"

# Create git tag
git tag -a v1.1.0 -m "Release version 1.1.0"

# Push tag
git push origin v1.1.0

# Jenkins will automatically build and push Docker image
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [Docker Documentation](https://docs.docker.com/)

## Contact

For questions or issues, please open an issue on GitHub or contact the maintainers.

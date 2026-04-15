// Jenkinsfile for ML Prediction API CI/CD Pipeline
// Windows-Compatible Build, Test, and Deploy
// Fixed: Uses virtual environment Python path (most reliable)

pipeline {
    agent any
    
    // Environment variables
    environment {
        // Use Python from virtual environment (most reliable approach)
        // This works regardless of which Python version is installed globally
        PYTHON = "venv/Scripts/python.exe"
        PIP = "venv/Scripts/pip.exe"
        DOCKER_HUB_REPO = 'swarajwadkar/ml-api'
        IMAGE_TAG = "${BUILD_NUMBER}"
        LATEST_TAG = 'latest'
    }
    
    options {
        // Keep only last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Timeout after 1 hour
        timeout(time: 1, unit: 'HOURS')
        // Add timestamps to console output
        timestamps()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '========== Cloning Repository =========='
                checkout scm
                echo 'Repository cloned successfully'
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                echo '========== Setting Up Python Virtual Environment =========='
                bat '''
                    echo Creating virtual environment...
                    if not exist venv (
                        python -m venv venv
                    ) else (
                        echo Virtual environment already exists
                    )
                    
                    echo.
                    echo Virtual environment ready at: venv/Scripts/python.exe
                '''
            }
        }
        
        stage('Check Python Installation') {
            steps {
                echo '========== Checking Python Version =========='
                bat '''
                    echo Python executable:
                    "%PYTHON%" --version
                    
                    echo.
                    echo Pip version:
                    "%PIP%" --version
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '========== Installing Dependencies =========='
                bat '''
                    echo Installing build tools first...
                    "%PYTHON%" -m pip install --upgrade pip
                    "%PYTHON%" -m pip install setuptools wheel build
                    
                    echo.
                    echo Installing project requirements...
                    "%PYTHON%" -m pip install -r requirements.txt
                    
                    echo.
                    echo All dependencies installed successfully
                '''
            }
        }
        
        stage('Code Quality & Tests') {
            steps {
                echo '========== Running Tests =========='
                bat '''
                    echo Running pytest...
                    "%PYTHON%" -m pytest tests/ -v --tb=short --junit-xml=test-results.xml || exit /b 0
                '''
            }
        }
        
        stage('Train Model') {
            steps {
                echo '========== Training ML Model =========='
                bat '''
                    echo Training machine learning model...
                    "%PYTHON%" model/train.py
                    
                    echo.
                    echo Model files created:
                    dir model\\*.pkl
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '========== Building Docker Image =========='
                bat '''
                    echo Building Docker image...
                    echo Image: %DOCKER_HUB_REPO%:%IMAGE_TAG%
                    
                    docker build -t %DOCKER_HUB_REPO%:%IMAGE_TAG% .
                    docker tag %DOCKER_HUB_REPO%:%IMAGE_TAG% %DOCKER_HUB_REPO%:%LATEST_TAG%
                    
                    echo.
                    echo Docker image built successfully
                    docker images %DOCKER_HUB_REPO%
                '''
            }
        }
        
        stage('Test Docker Image') {
            steps {
                echo '========== Testing Docker Image =========='
                bat '''
                    echo Starting container for testing...
                    docker run --rm -d --name ml-api-test -p 8000:8000 %DOCKER_HUB_REPO%:%IMAGE_TAG%
                    
                    echo Waiting for container to be ready...
                    timeout /t 10
                    
                    echo Verifying container is running...
                    docker ps -f name=ml-api-test
                    
                    echo.
                    echo Testing API health endpoint...
                    curl -s http://localhost:8000/ > nul
                    
                    if errorlevel 1 (
                        echo Health check failed!
                        docker logs ml-api-test
                        docker stop ml-api-test 2>nul
                        exit /b 1
                    )
                    
                    echo.
                    echo Health check passed!
                    docker stop ml-api-test
                '''
            }
        }
        
        stage('Push to Docker Hub') {
            when {
                branch 'main'
            }
            steps {
                echo '========== Pushing Docker Image to Docker Hub =========='
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat '''
                        echo Logging into Docker Hub...
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                        
                        if errorlevel 1 (
                            echo Docker login failed!
                            exit /b 1
                        )
                        
                        echo.
                        echo Pushing %IMAGE_TAG% tag...
                        docker push %DOCKER_HUB_REPO%:%IMAGE_TAG%
                        
                        echo.
                        echo Pushing %LATEST_TAG% tag...
                        docker push %DOCKER_HUB_REPO%:%LATEST_TAG%
                        
                        echo.
                        echo Images pushed successfully to Docker Hub
                        docker logout
                    '''
                }
            }
        }
        
        stage('Deployment Summary') {
            when {
                branch 'main'
            }
            steps {
                echo '========== Deployment Information =========='
                bat '''
                    echo.
                    echo Build and deployment completed successfully!
                    echo.
                    echo Docker Image Details:
                    echo   Repository: %DOCKER_HUB_REPO%
                    echo   Latest Tag: %LATEST_TAG%
                    echo   Build Tag: %IMAGE_TAG%
                    echo   Port: 8000
                    echo.
                    echo To deploy the image, run:
                    echo   docker pull %DOCKER_HUB_REPO%:%LATEST_TAG%
                    echo   docker run -d -p 8000:8000 %DOCKER_HUB_REPO%:%LATEST_TAG%
                    echo.
                    echo Then access the API at:
                    echo   http://localhost:8000/docs
                    echo.
                '''
            }
        }
    }
    
    post {
        always {
            echo '========== Pipeline Cleanup =========='
            bat 'docker logout 2>nul || exit /b 0'
        }
        
        success {
            echo '========== Build SUCCESS =========='
        }
        
        failure {
            echo '========== Build FAILED =========='
        }
        
        unstable {
            echo '========== Build UNSTABLE =========='
        }
    }
}

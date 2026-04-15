// Jenkinsfile for ML Prediction API CI/CD Pipeline
// Windows-Compatible Build, Test, and Deploy

pipeline {
    agent any
    
    // Environment variables
    environment {
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
        
        stage('Check Python Version') {
            steps {
                echo '========== Checking Python Version =========='
                bat '''
                    python --version
                    python -m pip --version
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '========== Installing Dependencies =========='
                bat '''
                    echo Installing dependencies...
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    echo Dependencies installed successfully
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo '========== Running Unit Tests =========='
                bat '''
                    echo Running pytest...
                    python -m pytest tests/ -v --tb=short --junit-xml=test-results.xml
                '''
            }
        }
        
        stage('Train Model') {
            steps {
                echo '========== Training ML Model =========='
                bat '''
                    echo Training model...
                    python model/train.py
                    dir model\
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '========== Building Docker Image =========='
                bat '''
                    echo Building Docker image: %DOCKER_HUB_REPO%:%IMAGE_TAG%
                    docker build -t %DOCKER_HUB_REPO%:%IMAGE_TAG% .
                    docker tag %DOCKER_HUB_REPO%:%IMAGE_TAG% %DOCKER_HUB_REPO%:%LATEST_TAG%
                    echo Docker image built successfully
                    echo Image details:
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
                    timeout /t 5 /nobreak
                    
                    echo Testing health endpoint...
                    curl -f http://localhost:8000/ || (docker stop ml-api-test && exit /b 1)
                    
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
                        
                        echo Pushing image: %DOCKER_HUB_REPO%:%IMAGE_TAG%
                        docker push %DOCKER_HUB_REPO%:%IMAGE_TAG%
                        
                        echo Pushing image: %DOCKER_HUB_REPO%:%LATEST_TAG%
                        docker push %DOCKER_HUB_REPO%:%LATEST_TAG%
                        
                        echo Images pushed successfully
                        docker logout
                    '''
                }
            }
        }
        
        stage('Deploy Instructions') {
            when {
                branch 'main'
            }
            steps {
                echo '========== Deployment Instructions =========='
                bat '''
                    echo Docker image successfully built and pushed to Docker Hub
                    echo.
                    echo Image: %DOCKER_HUB_REPO%:%LATEST_TAG%
                    echo Port: 8000
                    echo.
                    echo To deploy, run:
                    echo  docker pull %DOCKER_HUB_REPO%:%LATEST_TAG%
                    echo  docker run -d -p 8000:8000 %DOCKER_HUB_REPO%:%LATEST_TAG%
                    echo.
                    echo Then access API at: http://localhost:8000/docs
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
            echo '========== Pipeline SUCCESS! =========='
        }
        
        failure {
            echo '========== Pipeline FAILED! =========='
        }
        
        unstable {
            echo '========== Pipeline is UNSTABLE =========='
        }
    }
}

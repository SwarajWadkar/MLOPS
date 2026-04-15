// Jenkinsfile for ML Prediction API CI/CD Pipeline
// Build, test, and push Docker image to Docker Hub

pipeline {
    agent any
    
    // Environment variables
    environment {
        DOCKER_HUB_REPO = 'swarajwadkar/ml-api'
        DOCKER_HUB_CREDENTIALS = 'docker-hub-credentials'
        IMAGE_TAG = "${BUILD_NUMBER}"
        LATEST_TAG = 'latest'
        GIT_REPO = 'https://github.com/yourusername/mlops-pipeline.git'
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
                sh 'echo "Repository cloned successfully"'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '========== Installing Dependencies =========='
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    echo "Dependencies installed successfully"
                '''
            }
        }
        
        stage('Code Quality Checks') {
            steps {
                echo '========== Running Code Quality Checks =========='
                sh '''
                    echo "Running flake8 linting..."
                    flake8 app/ model/ tests/ --max-line-length=100 --ignore=E203,W503 || true
                    
                    echo "Running mypy type checking..."
                    mypy app/ model/ || true
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo '========== Running Unit Tests =========='
                sh '''
                    echo "Running pytest..."
                    python -m pytest tests/ -v --tb=short --junit-xml=test-results.xml || true
                '''
            }
        }
        
        stage('Train Model') {
            steps {
                echo '========== Training ML Model =========='
                sh '''
                    echo "Training model..."
                    python model/train.py
                    ls -lah model/
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '========== Building Docker Image =========='
                sh '''
                    echo "Building Docker image: ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
                    docker build -t ${DOCKER_HUB_REPO}:${IMAGE_TAG} .
                    docker tag ${DOCKER_HUB_REPO}:${IMAGE_TAG} ${DOCKER_HUB_REPO}:${LATEST_TAG}
                    echo "Docker image built successfully"
                    echo "Image size:"
                    docker images ${DOCKER_HUB_REPO}
                '''
            }
        }
        
        stage('Test Docker Image') {
            steps {
                echo '========== Testing Docker Image =========='
                sh '''
                    echo "Starting container for testing..."
                    docker run --rm -d --name ml-api-test -p 8000:8000 ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                    sleep 5
                    
                    echo "Testing health endpoint..."
                    curl -f http://localhost:8000/ || exit 1
                    
                    echo "Health check passed!"
                    docker stop ml-api-test || true
                '''
            }
        }
        
        stage('Push to Docker Hub') {
            when {
                branch 'main'
            }
            steps {
                echo '========== Pushing Docker Image to Docker Hub =========='
                sh '''
                    echo "Logging into Docker Hub..."
                    echo "${DOCKER_HUB_PASSWORD}" | docker login -u "${DOCKER_HUB_USERNAME}" --password-stdin
                    
                    echo "Pushing image: ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
                    docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                    
                    echo "Pushing image: ${DOCKER_HUB_REPO}:${LATEST_TAG}"
                    docker push ${DOCKER_HUB_REPO}:${LATEST_TAG}
                    
                    echo "Images pushed successfully"
                    docker logout
                '''
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo '========== Deployment Stage =========='
                sh '''
                    echo "Deployment configuration:"
                    echo "Image: ${DOCKER_HUB_REPO}:${LATEST_TAG}"
                    echo "Port: 8000"
                    echo ""
                    echo "To deploy, run:"
                    echo "docker pull ${DOCKER_HUB_REPO}:${LATEST_TAG}"
                    echo "docker run -d -p 8000:8000 ${DOCKER_HUB_REPO}:${LATEST_TAG}"
                '''
            }
        }
    }
    
    post {
        always {
            echo '========== Pipeline Cleanup =========='
            // Clean up
            sh 'docker logout || true'
            // Archive test results
            junit 'test-results.xml' || true
        }
        
        success {
            echo '========== Pipeline succeeded! =========='
        }
        
        failure {
            echo '========== Pipeline failed! =========='
            // Could add failure notifications here
        }
        
        unstable {
            echo '========== Pipeline is unstable =========='
        }
    }
}

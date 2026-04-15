# Jenkins Setup and Configuration Guide

## Prerequisites
- Jenkins running (version 2.361+ recommended)
- Docker installed on Jenkins agent
- Git plugin configured
- Pipeline plugin enabled

## Step 1: Create New Pipeline Job

1. Open Jenkins Dashboard
2. Click **New Item**
3. Enter job name: `ml-api-pipeline`
4. Select **Pipeline**
5. Click **Create**

## Step 2: Configure Pipeline

### General Tab
- Check "GitHub hook trigger for GITScm polling"
- Check "Discard old builds"
- Set Max # of builds to keep: 10

### Pipeline Tab
- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/yourusername/mlops-pipeline.git`
- **Credentials**: Select your Git credentials (create if needed)
- **Branch Specifier**: `*/main`
- **Script Path**: `Jenkinsfile`

## Step 3: Configure Docker Hub Credentials

### Add Credentials
1. Go to Jenkins > Manage Jenkins > Manage Credentials
2. Click on (global) domain
3. Click Add Credentials
4. Select Username with password
5. Enter:
   - **Username**: Your Docker Hub username
   - **Password**: Your Docker Hub access token
   - **ID**: `docker-hub-credentials`
6. Click Create

### Add Environment Variable
1. Go to Jenkins > Manage Jenkins > Configure System
2. Scroll to Global properties
3. Check "Environment variables"
4. Add:
   - **Name**: DOCKER_HUB_USERNAME
   - **Value**: your_docker_hub_username
5. Click Save

## Step 4: Set GitHub Webhook (Optional but Recommended)

### GitHub Side
1. Go to your repository settings
2. Navigate to Webhooks
3. Click Add webhook
4. **Payload URL**: `http://your-jenkins-url/github-webhook/`
5. **Content type**: application/json
6. Select events: Push events
7. Click Add webhook

### Jenkins Side
1. In job configuration
2. Build Triggers section
3. Check "GitHub hook trigger for GITScm polling"
4. Save

## Step 5: Run the Pipeline

### Manual Trigger
1. Open the job
2. Click "Build Now"
3. View progress in build logs

### Automatic Trigger
Push to main branch to trigger automatically (if webhook configured)

## Pipeline Stages Explanation

### 1. Checkout
- Clones the repository
- Checks out specified branch

### 2. Install Dependencies
- Upgrades pip
- Installs Python packages from requirements.txt

### 3. Code Quality Checks
- Runs flake8 linting
- Runs mypy type checking
- Non-blocking (doesn't fail build)

### 4. Unit Tests
- Runs pytest suite
- Generates test-results.xml
- Non-blocking (doesn't fail build)

### 5. Train Model
- Trains ML model
- Saves model and scaler files

### 6. Build Docker Image
- Builds Docker image with tag: `swarajwadkar/ml-api:${BUILD_NUMBER}`
- Also tags as `swarajwadkar/ml-api:latest`

### 7. Test Docker Image
- Starts container
- Performs health check
- Stops container

### 8. Push to Docker Hub
- Only runs on `main` branch
- Logs into Docker Hub
- Pushes both tagged images
- Logs out

### 9. Deploy
- Prints deployment instructions
- Can be extended for actual deployment

## Troubleshooting

### Docker Not Found
```groovy
// Add to Jenkinsfile
sh 'which docker'
sh 'docker --version'
```

### Permission Denied
```bash
# Run Jenkins user with docker access
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Model Training Fails
- Check Python version (3.9+)
- Check available disk space
- Verify all dependencies installed

### Docker Push Fails
- Verify Docker Hub credentials
- Check network connectivity
- Verify user has push permissions

### Build Timeout
- Increase timeout in Jenkinsfile (currently 1 hour)
- Check for slow network
- Check system resources

## Useful Jenkins Commands

### View Console Output
```bash
# From Jenkins UI: Click on build number > Console Output
```

### Restart Jenkins
```bash
sudo systemctl restart jenkins
```

### View Jenkins Logs
```bash
sudo tail -f /var/log/jenkins/jenkins.log
```

## Advanced Configuration

### Send Build Notifications
Add to Jenkinsfile post section:
```groovy
post {
    always {
        emailext(
            subject: "Build ${BUILD_NUMBER}: ${BUILD_STATUS}",
            body: "See ${BUILD_URL}console",
            to: "your-email@example.com"
        )
    }
}
```

### Parallel Test Execution
```groovy
parallel {
    stage('Unit Tests') {
        steps { sh 'pytest tests/test_api.py' }
    }
    stage('Integration Tests') {
        steps { sh 'pytest tests/test_integration.py' }
    }
}
```

### Slack Integration
1. Install Jenkins Slack plugin
2. Configure Slack webhook
3. Add to Jenkinsfile:
```groovy
slackSend(
    color: 'good',
    message: "Build succeeded: ${BUILD_URL}"
)
```

## Security Best Practices

1. **Store secrets in Jenkins Credentials**
   - Never hardcode passwords
   - Use credential plugins

2. **Use Jenkins Pipeline Best Practices**
   - Declare all variables
   - Use parameterized builds
   - Version control Jenkinsfile

3. **Docker Security**
   - Run containers as non-root user
   - Scan images for vulnerabilities
   - Use minimal base images

4. **Access Control**
   - Enable Jenkins authentication
   - Use role-based access control
   - Audit user actions

## Performance Optimization

### Cache Docker Layers
```bash
# Dockerfile should have build steps in optimal order
# Most frequently changes go last
```

### Parallel Stages
```groovy
// Run independent stages in parallel
parallel(
    "Code Quality": { sh 'flake8 .' },
    "Type Check": { sh 'mypy .' },
    "Security Scan": { sh 'bandit .' }
)
```

### Build Agents
- Use dedicated agents for Docker builds
- Scale horizontally with additional agents

## Monitoring and Logging

### View Build Statistics
1. Jenkins Dashboard
2. Job name > Trends
3. View success rate and duration trends

### Build Logs
- Available in Jenkins UI
- Also saved to disk
- Can be archived to external storage

## References
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Docker Plugin for Jenkins](https://plugins.jenkins.io/docker/)
- [GitHub Integration Plugin](https://plugins.jenkins.io/github/)

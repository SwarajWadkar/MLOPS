@echo off
REM Docker build and tag script for Windows

setlocal enabledelayedexpansion

echo ======================================
echo Docker Build Script
echo ======================================

REM Configuration
set DOCKER_HUB_USERNAME=swarajwadkar
set REPO_NAME=ml-api
set IMAGE_NAME=%DOCKER_HUB_USERNAME%/%REPO_NAME%

REM Get timestamp for build tag
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set BUILD_TAG=%mydate%%mytime%
set LATEST_TAG=latest

echo.
echo Building Docker image...
echo Image: %IMAGE_NAME%:%BUILD_TAG%
echo.

REM Build image
docker build -t %IMAGE_NAME%:%BUILD_TAG% .
if errorlevel 1 (
    echo Error: Docker build failed
    exit /b 1
)

docker tag %IMAGE_NAME%:%BUILD_TAG% %IMAGE_NAME%:%LATEST_TAG%

echo.
echo Successfully built Docker images:
docker images %IMAGE_NAME%

echo.
echo ======================================
echo To push to Docker Hub, run:
echo   docker push %IMAGE_NAME%:%BUILD_TAG%
echo   docker push %IMAGE_NAME%:%LATEST_TAG%
echo.
echo To run locally:
echo   docker run -p 8000:8000 %IMAGE_NAME%:%LATEST_TAG%
echo ======================================

@echo off
REM Docker push script for Windows

setlocal enabledelayedexpansion

set DOCKER_HUB_USERNAME=swarajwadkar
set REPO_NAME=ml-api
set IMAGE_NAME=%DOCKER_HUB_USERNAME%/%REPO_NAME%
set TAG=%1
if "!TAG!"=="" (set TAG=latest)

echo ======================================
echo Docker Push Script
echo ======================================
echo Pushing %IMAGE_NAME%:%TAG%
echo.

REM Check if Docker credentials are set
if "!DOCKER_HUB_USERNAME!"=="" (
    echo Error: DOCKER_HUB_USERNAME not set
    echo Please run:
    echo   set DOCKER_HUB_USERNAME=your_username
    echo   set DOCKER_HUB_PASSWORD=your_password
    exit /b 1
)

if "!DOCKER_HUB_PASSWORD!"=="" (
    echo Error: DOCKER_HUB_PASSWORD not set
    echo Please set your Docker Hub password first:
    echo   set DOCKER_HUB_PASSWORD=your_password
    exit /b 1
)

REM Login to Docker Hub
echo Logging into Docker Hub...
echo !DOCKER_HUB_PASSWORD! | docker login -u !DOCKER_HUB_USERNAME! --password-stdin

if errorlevel 1 (
    echo Error: Docker login failed
    exit /b 1
)

REM Push image
echo Pushing image...
docker push %IMAGE_NAME%:%TAG%

if errorlevel 1 (
    echo Error: Docker push failed
    docker logout
    exit /b 1
)

echo.
echo Pushing completed successfully
echo.

REM Logout
docker logout

echo.
echo ======================================
echo Image pushed: %IMAGE_NAME%:%TAG%
echo ======================================

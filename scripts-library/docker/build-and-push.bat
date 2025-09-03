@echo off
REM scripts-library/docker/build-and-push.bat
REM Universal Docker build and push script for Windows

set "DOCKERHUB_USERNAME=%1"
set "IMAGE_NAME=%2"
set "IMAGE_TAG=%3"

if "%IMAGE_TAG%"=="" set "IMAGE_TAG=latest"

if "%DOCKERHUB_USERNAME%"=="" (
    echo Usage: build-and-push.bat ^<dockerhub-username^> ^<image-name^> [tag]
    echo Example: build-and-push.bat myuser my-app latest
    exit /b 1
)

if "%IMAGE_NAME%"=="" (
    echo Usage: build-and-push.bat ^<dockerhub-username^> ^<image-name^> [tag]
    echo Example: build-and-push.bat myuser my-app latest
    exit /b 1
)

set "FULL_IMAGE_NAME=docker.io/%DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%"

echo 🐳 Building and pushing: %FULL_IMAGE_NAME%

docker buildx build --platform linux/amd64,linux/arm64 -t "%FULL_IMAGE_NAME%" --push .

if %errorlevel% equ 0 (
    echo ✅ Successfully built and pushed: %FULL_IMAGE_NAME%
) else (
    echo ❌ Build/push failed
    exit /b 1
)
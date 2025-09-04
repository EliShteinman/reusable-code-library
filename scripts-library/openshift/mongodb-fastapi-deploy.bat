@echo off
setlocal EnableDelayedExpansion

@REM ================================================================================
@REM  Universal FastAPI MongoDB Deployment Script for OpenShift (Generic Version)
@REM ================================================================================

@REM === Configuration ===
set "DOCKERHUB_USERNAME=%1"
set "PROJECT_NAME=%2"
set "APP_NAME=%3"
set "DEPLOYMENT_TYPE=%4"
set "MONGO_DB_NAME=%5"
set "MONGO_COLLECTION_NAME=%6"

if "%~6"=="" (
    echo [ERROR] Usage: mongodb-fastapi-deploy.bat ^<dockerhub-username^> ^<project-name^> ^<app-name^> ^<deployment-type^> ^<db-name^> ^<collection-name^>
    echo [INFO] deployment-type: standard ^| statefulset
    echo [EXAMPLE] mongodb-fastapi-deploy.bat myuser my-project soldiers-api standard enemy_soldiers soldier_details
    exit /b 1
)

for /f "tokens=*" %%g in ('git rev-parse --short HEAD 2^>nul') do set "IMAGE_TAG=%%g"
if not defined IMAGE_TAG (
    for /f "tokens=*" %%g in ('powershell -Command "Get-Date -UFormat +%%s"') do set "IMAGE_TAG=%%g"
)

@REM Default Settings
set "MONGO_IMAGE=mongo:8.0"
set "MONGO_USER=mongoadmin"
set "MONGO_PASSWORD=yourSecurePasswordChangeMe"
set "STORAGE_SIZE=2Gi"
set "FULL_IMAGE_NAME=docker.io/%DOCKERHUB_USERNAME%/%APP_NAME%:%IMAGE_TAG%"
set "API_PORT=8080"
set "MONGO_PORT=27017"
set "APP_MODULE_PATH=services.data_loader.main"
set "APP_VARIABLE_NAME=app"

@REM Resource settings
set "MONGO_CPU_REQUEST=200m"
set "MONGO_MEMORY_REQUEST=256Mi"
set "MONGO_CPU_LIMIT=500m"
set "MONGO_MEMORY_LIMIT=512Mi"
set "API_CPU_REQUEST=50m"
set "API_MEMORY_REQUEST=128Mi"
set "API_CPU_LIMIT=200m"
set "API_MEMORY_LIMIT=256Mi"

echo [INFO] Starting %DEPLOYMENT_TYPE% deployment for project: %PROJECT_NAME%...

@REM === Step 1: Build & Push ===
echo.
echo [INFO] Building and pushing Docker image...
docker buildx build --no-cache --platform linux/amd64,linux/arm64 -t "%FULL_IMAGE_NAME%" --build-arg APP_MODULE=%APP_MODULE_PATH% --push .
if !errorlevel! neq 0 (
    echo [ERROR] Docker build failed
    exit /b 1
)

@REM === Step 2: Setup Project ===
echo.
echo [INFO] Setting up OpenShift project...
oc delete project %PROJECT_NAME% --ignore-not-found=true
timeout /t 10 >nul
oc new-project %PROJECT_NAME%
oc project %PROJECT_NAME%

@REM === Step 3: Deploy Database ===
echo.
echo [INFO] Deploying MongoDB (%DEPLOYMENT_TYPE% approach)...
oc create configmap mongo-db-config --from-literal=MONGO_INITDB_ROOT_USERNAME=%MONGO_USER% --from-literal=MONGO_DB_NAME=%MONGO_DB_NAME% --from-literal=MONGO_COLLECTION_NAME=%MONGO_COLLECTION_NAME%
oc create secret generic mongo-db-credentials --from-literal=MONGO_INITDB_ROOT_PASSWORD=%MONGO_PASSWORD%

set "MONGO_TEMPLATE_PATH=..\..\kubernetes-templates\databases\mongodb\deployment-complete.yaml"
if /i "%DEPLOYMENT_TYPE%"=="statefulset" set "MONGO_TEMPLATE_PATH=..\..\kubernetes-templates\databases\mongodb\statefulset-complete.yaml"

powershell -Command "(Get-Content -Raw '%MONGO_TEMPLATE_PATH%') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${DATABASE_NAME}', '%MONGO_DB_NAME%' -replace '\${COLLECTION_NAME}', '%MONGO_COLLECTION_NAME%' -replace '\${MONGO_VERSION}', '8.0' -replace '\${STORAGE_SIZE}', '%STORAGE_SIZE%' -replace '\${MONGO_ROOT_PASSWORD}', '%MONGO_PASSWORD%' -replace '\${MONGO_CPU_REQUEST}', '%MONGO_CPU_REQUEST%' -replace '\${MONGO_MEMORY_REQUEST}', '%MONGO_MEMORY_REQUEST%' -replace '\${MONGO_CPU_LIMIT}', '%MONGO_CPU_LIMIT%' -replace '\${MONGO_MEMORY_LIMIT}', '%MONGO_MEMORY_LIMIT%' | oc apply -f -"

set "MONGO_SERVICE_NAME=%APP_NAME%-mongo-service"

echo [INFO] Waiting for MongoDB to be ready...
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=%APP_NAME%-mongo --timeout=300s
if !errorlevel! neq 0 (
    echo [ERROR] MongoDB failed to start
    exit /b 1
)
timeout /t 15 /nobreak >nul

@REM === Step 4: Deploy FastAPI ===
echo.
echo [INFO] Deploying FastAPI application...
powershell -Command "(Get-Content -Raw '..\..\kubernetes-templates\applications\fastapi-deployment.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${DOCKER_IMAGE}', '%DOCKERHUB_USERNAME%/%APP_NAME%' -replace '\${IMAGE_TAG}', '%IMAGE_TAG%' -replace '\${API_PORT}', '%API_PORT%' -replace '\${DB_PORT}', '%MONGO_PORT%' -replace '\${API_REPLICAS}', '1' -replace '\${API_CPU_REQUEST}', '%API_CPU_REQUEST%' -replace '\${API_MEMORY_REQUEST}', '%API_MEMORY_REQUEST%' -replace '\${API_CPU_LIMIT}', '%API_CPU_LIMIT%' -replace '\${API_MEMORY_LIMIT}', '%API_MEMORY_LIMIT%' | oc apply -f -"
powershell -Command "(Get-Content -Raw '..\..\kubernetes-templates\applications\fastapi-service.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${API_PORT}', '%API_PORT%' | oc apply -f -"
powershell -Command "(Get-Content -Raw '..\..\kubernetes-templates\applications\route.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${API_PORT}', '%API_PORT%' | oc apply -f -"

echo [INFO] Waiting for FastAPI to be ready...
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=%APP_NAME%-api --timeout=300s
if !errorlevel! neq 0 (
    echo [ERROR] FastAPI failed to start
    exit /b 1
)

@REM === Step 5: Final Output ===
echo.
echo ================================================================
echo                    DEPLOYMENT SUCCESSFUL
echo ================================================================
for /f "tokens=*" %%g in ('oc get route %APP_NAME%-api-route -o jsonpath="{.spec.host}"') do set "ROUTE_URL=%%g"
echo Project: %PROJECT_NAME%
echo App Name: %APP_NAME%
echo Application URL: https://!ROUTE_URL!
echo API Docs: https://!ROUTE_URL!/docs
echo ================================================================

endlocal
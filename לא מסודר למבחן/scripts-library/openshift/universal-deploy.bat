@REM scripts-library/openshift/universal-deploy.bat
@echo off
setlocal EnableDelayedExpansion

@REM === הגדרת משתנים ===
set "DOCKERHUB_USERNAME=%1"
set "PROJECT_NAME=%2"
set "APP_NAME=%3"

if "%~3"=="" (
    echo [ERROR] Usage: universal-deploy.bat ^<dockerhub-username^> ^<project-name^> ^<app-name^>
    echo [EXAMPLE] universal-deploy.bat myuser my-exam-project data-loader
    exit /b 1
)

@REM יצירת תג ייחודי
for /f "tokens=*" %%g in ('git rev-parse --short HEAD 2^>nul') do set "IMAGE_TAG=%%g"
if not defined IMAGE_TAG (
    for /f "tokens=*" %%g in ('powershell -Command "Get-Date -UFormat +%%s"') do set "IMAGE_TAG=%%g"
)

@REM הגדרת משתני ברירת מחדל
set "FULL_IMAGE_NAME=docker.io/%DOCKERHUB_USERNAME%/%APP_NAME%:%IMAGE_TAG%"
set "DATABASE_NAME=mydatabase"
set "DATABASE_USER=myuser"
set "MYSQL_ROOT_PASSWORD=rootpassword123"
set "MYSQL_PASSWORD=userpassword123"
set "STORAGE_SIZE=1Gi"
set "MYSQL_VERSION=8.0"
set "API_PORT=8080"
set "DB_PORT=3306"
set "API_REPLICAS=1"

@REM משאבי CPU וזיכרון
set "MYSQL_CPU_REQUEST=100m"
set "MYSQL_MEMORY_REQUEST=256Mi"
set "MYSQL_CPU_LIMIT=500m"
set "MYSQL_MEMORY_LIMIT=512Mi"
set "API_CPU_REQUEST=50m"
set "API_MEMORY_REQUEST=128Mi"
set "API_CPU_LIMIT=200m"
set "API_MEMORY_LIMIT=256Mi"

echo [INFO] Starting deployment for project: %PROJECT_NAME%
echo [INFO] App name: %APP_NAME%
echo [INFO] Image: %FULL_IMAGE_NAME%

@REM === שלב 1: בניה ועלאה ===
echo.
echo [INFO] Building and pushing Docker image...
docker buildx build --no-cache --platform linux/amd64,linux/arm64 -t "%FULL_IMAGE_NAME%" --push .
if !errorlevel! neq 0 (
    echo [ERROR] Docker build failed
    exit /b 1
)

@REM === שלב 2: יצירת פרויקט ===
echo.
echo [INFO] Setting up OpenShift project...
oc delete project %PROJECT_NAME% 2>nul
timeout /t 10 >nul
oc new-project %PROJECT_NAME%
oc project %PROJECT_NAME%

@REM === שלב 3: פריסת מסד נתונים ===
echo.
echo [INFO] Deploying database...
@REM החלפת משתנים ב-YAML ויישום
powershell -Command "
$configmap = (Get-Content -Raw 'templates\mysql-configmap.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${DATABASE_NAME}', '%DATABASE_NAME%' -replace '\${DATABASE_USER}', '%DATABASE_USER%'
$configmap | oc apply -f -
$secret = (Get-Content -Raw 'templates\mysql-secret.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${MYSQL_ROOT_PASSWORD}', '%MYSQL_ROOT_PASSWORD%' -replace '\${MYSQL_PASSWORD}', '%MYSQL_PASSWORD%'
$secret | oc apply -f -
$pvc = (Get-Content -Raw 'templates\mysql-pvc.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${STORAGE_SIZE}', '%STORAGE_SIZE%'
$pvc | oc apply -f -
$deployment = (Get-Content -Raw 'templates\mysql-deployment.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${MYSQL_VERSION}', '%MYSQL_VERSION%' -replace '\${MYSQL_CPU_REQUEST}', '%MYSQL_CPU_REQUEST%' -replace '\${MYSQL_MEMORY_REQUEST}', '%MYSQL_MEMORY_REQUEST%' -replace '\${MYSQL_CPU_LIMIT}', '%MYSQL_CPU_LIMIT%' -replace '\${MYSQL_MEMORY_LIMIT}', '%MYSQL_MEMORY_LIMIT%'
$deployment | oc apply -f -
$service = (Get-Content -Raw 'templates\mysql-service.yaml') -replace '\${APP_NAME}', '%APP_NAME%'
$service | oc apply -f -
"

echo [INFO] Waiting for database to be ready...
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=%APP_NAME%-mysql --timeout=300s
if !errorlevel! neq 0 (
    echo [ERROR] Database failed to start
    exit /b 1
)

@REM === שלב 4: פריסת API ===
echo.
echo [INFO] Deploying API application...
powershell -Command "
$deployment = (Get-Content -Raw 'templates\fastapi-deployment.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${DOCKER_IMAGE}', 'docker.io/%DOCKERHUB_USERNAME%/%APP_NAME%' -replace '\${IMAGE_TAG}', '%IMAGE_TAG%' -replace '\${API_PORT}', '%API_PORT%' -replace '\${DB_PORT}', '%DB_PORT%' -replace '\${API_REPLICAS}', '%API_REPLICAS%' -replace '\${API_CPU_REQUEST}', '%API_CPU_REQUEST%' -replace '\${API_MEMORY_REQUEST}', '%API_MEMORY_REQUEST%' -replace '\${API_CPU_LIMIT}', '%API_CPU_LIMIT%' -replace '\${API_MEMORY_LIMIT}', '%API_MEMORY_LIMIT%'
$deployment | oc apply -f -
$service = (Get-Content -Raw 'templates\fastapi-service.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${API_PORT}', '%API_PORT%'
$service | oc apply -f -
$route = (Get-Content -Raw 'templates\route.yaml') -replace '\${APP_NAME}', '%APP_NAME%' -replace '\${API_PORT}', '%API_PORT%'
$route | oc apply -f -
"

echo [INFO] Waiting for API to be ready...
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=%APP_NAME%-api --timeout=300s
if !errorlevel! neq 0 (
    echo [ERROR] API failed to start
    exit /b 1
)

@REM === שלב 5: אתחול נתונים ===
echo.
echo [INFO] Initializing database data...
for /f "tokens=*" %%g in ('oc get pod -l app.kubernetes.io/instance=%APP_NAME%-mysql -o jsonpath="{.items[0].metadata.name}"') do set "MYSQL_POD=%%g"
echo [INFO] Found MySQL pod: !MYSQL_POD!

if exist "scripts\create_data.sql" (
    oc exec -i "!MYSQL_POD!" -- mysql -u root -p"%MYSQL_ROOT_PASSWORD%" %DATABASE_NAME% < scripts\create_data.sql
)
if exist "scripts\insert_data.sql" (
    oc exec -i "!MYSQL_POD!" -- mysql -u root -p"%MYSQL_ROOT_PASSWORD%" %DATABASE_NAME% < scripts\insert_data.sql
)

@REM === שלב 6: הצגת התוצאות ===
echo.
echo ================================================================
echo                    DEPLOYMENT SUCCESSFUL
echo ================================================================
for /f "tokens=*" %%g in ('oc get route %APP_NAME%-api-route -o jsonpath="{.spec.host}"') do set "ROUTE_URL=%%g"
echo Project: %PROJECT_NAME%
echo App Name: %APP_NAME%
echo Application URL: https://!ROUTE_URL!
echo Data Endpoint: https://!ROUTE_URL!/data
echo API Docs: https://!ROUTE_URL!/docs
echo ================================================================

endlocal
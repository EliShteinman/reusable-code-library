# scripts-library/openshift/mongodb-fastapi-deploy.bat
@echo off
setlocal EnableDelayedExpansion

@REM ================================================================================
@REM  Universal FastAPI MongoDB Deployment Script for OpenShift
@REM  Based on the advanced patterns from the exam solution
@REM ================================================================================

@REM === הגדרת משתנים ===
set "DOCKERHUB_USERNAME=%1"
set "PROJECT_NAME=%2"
set "APP_NAME=%3"
set "DEPLOYMENT_TYPE=%4"

if "%~4"=="" (
    echo [ERROR] Usage: mongodb-fastapi-deploy.bat ^<dockerhub-username^> ^<project-name^> ^<app-name^> ^<deployment-type^>
    echo [INFO] deployment-type: standard ^| statefulset
    echo [EXAMPLE] mongodb-fastapi-deploy.bat myuser my-exam-project soldiers-api standard
    exit /b 1
)

@REM יצירת תג ייחודי
for /f "tokens=*" %%g in ('git rev-parse --short HEAD 2^>nul') do set "IMAGE_TAG=%%g"
if not defined IMAGE_TAG (
    for /f "tokens=*" %%g in ('powershell -Command "Get-Date -UFormat +%%s"') do set "IMAGE_TAG=%%g"
)

@REM הגדרות MongoDB
set "MONGO_IMAGE=mongo:8.0"
set "MONGO_DB_NAME=enemy_soldiers"
set "MONGO_COLLECTION_NAME=soldier_details"
set "MONGO_USER=mongoadmin"
set "MONGO_PASSWORD=jhsdyttfe65fds54scf65"
set "STORAGE_SIZE=2Gi"

@REM הגדרות FastAPI
set "FULL_IMAGE_NAME=docker.io/%DOCKERHUB_USERNAME%/%APP_NAME%:%IMAGE_TAG%"
set "API_PORT=8080"
set "MONGO_PORT=27017"

@REM משאבי CPU וזיכרון
set "MONGO_CPU_REQUEST=200m"
set "MONGO_MEMORY_REQUEST=256Mi"
set "MONGO_CPU_LIMIT=500m"
set "MONGO_MEMORY_LIMIT=512Mi"
set "API_CPU_REQUEST=50m"
set "API_MEMORY_REQUEST=128Mi"
set "API_CPU_LIMIT=200m"
set "API_MEMORY_LIMIT=256Mi"

echo [INFO] Starting %DEPLOYMENT_TYPE% deployment for project: %PROJECT_NAME%
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
echo [INFO] Deploying MongoDB (%DEPLOYMENT_TYPE% approach)...

@REM יצירת ConfigMap
oc create configmap mongo-db-config ^
  --from-literal=MONGO_INITDB_ROOT_USERNAME=%MONGO_USER% ^
  --from-literal=MONGO_DB_NAME=%MONGO_DB_NAME% ^
  --from-literal=MONGO_COLLECTION_NAME=%MONGO_COLLECTION_NAME%

@REM יצירת Secret
oc create secret generic mongo-db-credentials ^
  --from-literal=MONGO_INITDB_ROOT_PASSWORD=%MONGO_PASSWORD%

if /i "%DEPLOYMENT_TYPE%"=="statefulset" goto :deploy_statefulset
if /i "%DEPLOYMENT_TYPE%"=="standard" goto :deploy_standard
echo [ERROR] Invalid deployment type: %DEPLOYMENT_TYPE%
exit /b 1

:deploy_standard
echo [INFO] Using standard Deployment approach...

@REM יצירת PVC נפרד
(
echo apiVersion: v1
echo kind: PersistentVolumeClaim
echo metadata:
echo   name: %APP_NAME%-mongo-pvc
echo   labels:
echo     app.kubernetes.io/name: mongo
echo     app.kubernetes.io/instance: %APP_NAME%-mongo
echo     app.kubernetes.io/part-of: %APP_NAME%
echo spec:
echo   accessModes:
echo     - ReadWriteOnce
echo   resources:
echo     requests:
echo       storage: %STORAGE_SIZE%
) | oc apply -f -

@REM MongoDB Deployment
(
echo apiVersion: apps/v1
echo kind: Deployment
echo metadata:
echo   name: %APP_NAME%-mongo-deployment
echo   labels:
echo     app.kubernetes.io/name: mongo
echo     app.kubernetes.io/instance: %APP_NAME%-mongo
echo     app.kubernetes.io/part-of: %APP_NAME%
echo spec:
echo   replicas: 1
echo   selector:
echo     matchLabels:
echo       app.kubernetes.io/instance: %APP_NAME%-mongo
echo   template:
echo     metadata:
echo       labels:
echo         app.kubernetes.io/name: mongo
echo         app.kubernetes.io/instance: %APP_NAME%-mongo
echo         app.kubernetes.io/part-of: %APP_NAME%
echo     spec:
echo       containers:
echo         - name: mongo
echo           image: %MONGO_IMAGE%
echo           ports:
echo             - containerPort: 27017
echo           envFrom:
echo             - configMapRef:
echo                 name: mongo-db-config
echo             - secretRef:
echo                 name: mongo-db-credentials
echo           resources:
echo             requests:
echo               cpu: "%MONGO_CPU_REQUEST%"
echo               memory: "%MONGO_MEMORY_REQUEST%"
echo             limits:
echo               cpu: "%MONGO_CPU_LIMIT%"
echo               memory: "%MONGO_MEMORY_LIMIT%"
echo           volumeMounts:
echo             - name: mongo-persistent-storage
echo               mountPath: /data/db
echo       volumes:
echo         - name: mongo-persistent-storage
echo           persistentVolumeClaim:
echo             claimName: %APP_NAME%-mongo-pvc
) | oc apply -f -

@REM MongoDB Service
(
echo apiVersion: v1
echo kind: Service
echo metadata:
echo   name: %APP_NAME%-mongo-service
echo   labels:
echo     app.kubernetes.io/name: mongo
echo     app.kubernetes.io/instance: %APP_NAME%-mongo
echo     app.kubernetes.io/part-of: %APP_NAME%
echo spec:
echo   selector:
echo     app.kubernetes.io/instance: %APP_NAME%-mongo
echo   ports:
echo     - protocol: TCP
echo       port: 27017
echo       targetPort: 27017
) | oc apply -f -

set "MONGO_SERVICE_NAME=%APP_NAME%-mongo-service"
goto :deploy_api

:deploy_statefulset
echo [INFO] Using StatefulSet approach...

@REM MongoDB StatefulSet
(
echo apiVersion: apps/v1
echo kind: StatefulSet
echo metadata:
echo   name: %APP_NAME%-mongo-statefulset
echo   labels:
echo     app.kubernetes.io/name: mongo
echo     app.kubernetes.io/instance: %APP_NAME%-mongo
echo     app.kubernetes.io/part-of: %APP_NAME%
echo spec:
echo   serviceName: "%APP_NAME%-mongo-headless-service"
echo   replicas: 1
echo   selector:
echo     matchLabels:
echo       app.kubernetes.io/instance: %APP_NAME%-mongo
echo   template:
echo     metadata:
echo       labels:
echo         app.kubernetes.io/name: mongo
echo         app.kubernetes.io/instance: %APP_NAME%-mongo
echo         app.kubernetes.io/part-of: %APP_NAME%
echo     spec:
echo       containers:
echo         - name: mongo
echo           image: %MONGO_IMAGE%
echo           ports:
echo             - containerPort: 27017
echo           envFrom:
echo             - configMapRef:
echo                 name: mongo-db-config
echo             - secretRef:
echo                 name: mongo-db-credentials
echo           resources:
echo             requests:
echo               cpu: "%MONGO_CPU_REQUEST%"
echo               memory: "%MONGO_MEMORY_REQUEST%"
echo             limits:
echo               cpu: "%MONGO_CPU_LIMIT%"
echo               memory: "%MONGO_MEMORY_LIMIT%"
echo           volumeMounts:
echo             - name: mongo-persistent-storage
echo               mountPath: /data/db
echo   volumeClaimTemplates:
echo   - metadata:
echo       name: mongo-persistent-storage
echo       labels:
echo         app.kubernetes.io/part-of: %APP_NAME%
echo     spec:
echo       accessModes: [ "ReadWriteOnce" ]
echo       resources:
echo         requests:
echo           storage: %STORAGE_SIZE%
) | oc apply -f -

@REM Headless Service עבור StatefulSet
(
echo apiVersion: v1
echo kind: Service
echo metadata:
echo   name: %APP_NAME%-mongo-headless-service
echo   labels:
echo     app.kubernetes.io/name: mongo
echo     app.kubernetes.io/instance: %APP_NAME%-mongo
echo     app.kubernetes.io/part-of: %APP_NAME%
echo spec:
echo   clusterIP: None
echo   selector:
echo     app.kubernetes.io/instance: %APP_NAME%-mongo
echo   ports:
echo     - protocol: TCP
echo       port: 27017
echo       targetPort: 27017
) | oc apply -f -

set "MONGO_SERVICE_NAME=%APP_NAME%-mongo-headless-service"

:deploy_api
echo [INFO] Waiting for MongoDB to be ready...
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=%APP_NAME%-mongo --timeout=300s
if !errorlevel! neq 0 (
    echo [ERROR] MongoDB failed to start
    exit /b 1
)
timeout /t 15 /nobreak >nul

@REM === שלב 4: פריסת FastAPI ===
echo.
echo [INFO] Deploying FastAPI application...

@REM FastAPI Deployment
(
echo apiVersion: apps/v1
echo kind: Deployment
echo metadata:
echo   name: %APP_NAME%-api-deployment
echo   labels:
echo     app.kubernetes.io/name: fastapi-mongo
echo     app.kubernetes.io/instance: %APP_NAME%-api
echo     app.kubernetes.io/part-of: %APP_NAME%
echo spec:
echo   replicas: 1
echo   selector:
echo     matchLabels:
echo       app.kubernetes.io/instance: %APP_NAME%-api
echo   template:
echo     metadata:
echo       labels:
echo         app.kubernetes.io/name: fastapi-mongo
echo         app.kubernetes.io/instance: %APP_NAME%-api
echo         app.kubernetes.io/part-of: %APP_NAME%
echo     spec:
echo       containers:
echo         - name: fastapi-container
echo           image: "%FULL_IMAGE_NAME%"
echo           imagePullPolicy: Always
echo           ports:
echo             - containerPort: %API_PORT%
echo           env:
echo             - name: MONGO_HOST
echo               value: "%MONGO_SERVICE_NAME%"
echo             - name: MONGO_PORT
echo               value: "%MONGO_PORT%"
echo             - name: MONGO_DB_NAME
echo               valueFrom:
echo                 configMapKeyRef:
echo                   name: mongo-db-config
echo                   key: MONGO_DB_NAME
echo             - name: MONGO_USER
echo               valueFrom:
echo                 configMapKeyRef:
echo                   name: mongo-db-config
echo                   key: MONGO_INITDB_ROOT_USERNAME
echo             - name: MONGO_PASSWORD
echo               valueFrom:
echo                 secretKeyRef:
echo                   name: mongo-db-credentials
echo                   key: MONGO_INITDB_ROOT_PASSWORD
echo             - name: MONGO_COLLECTION_NAME
echo               valueFrom:
echo                 configMapKeyRef:
echo                   name: mongo-db-config
echo                   key: MONGO_COLLECTION_NAME
echo           readinessProbe:
echo             httpGet:
echo               path: /health
echo               port: %API_PORT%
echo             initialDelaySeconds: 15
echo             periodSeconds: 10
echo           livenessProbe:
echo             httpGet:
echo               path: /
echo               port: %API_PORT%
echo             initialDelaySeconds: 20
echo             periodSeconds: 20
echo           resources:
echo             requests:
echo               cpu: "%API_CPU_REQUEST%"
echo               memory: "%API_MEMORY_REQUEST%"
echo             limits:
echo               cpu: "%API_CPU_LIMIT%"
echo               memory: "%API_MEMORY_LIMIT%"
) | oc apply -f -

@REM FastAPI Service
(
echo apiVersion: v1
echo kind: Service
echo metadata:
echo   name: %APP_NAME%-api-service
echo   labels:
echo     app.kubernetes.io/name: fastapi-mongo
echo     app.kubernetes.io/instance: %APP_NAME%-api
echo     app.kubernetes.io/part-of: %APP_NAME%
echo spec:
echo   selector:
echo     app.kubernetes.io/instance: %APP_NAME%-api
echo   ports:
echo     - protocol: TCP
echo       port: %API_PORT%
echo       targetPort: %API_PORT%
echo   type: ClusterIP
) | oc apply -f -

echo [INFO] Waiting for FastAPI to be ready...
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=%APP_NAME%-api --timeout=300s
if !errorlevel! neq 0 (
    echo [ERROR] FastAPI failed to start
    exit /b 1
)

@REM === שלב 5: חשיפה ציבורית ===
echo.
echo [INFO] Creating public route...

@REM Route
(
echo apiVersion: route.openshift.io/v1
echo kind: Route
echo metadata:
echo   name: %APP_NAME%-api-route
echo   labels:
echo     app.kubernetes.io/name: fastapi-mongo
echo     app.kubernetes.io/instance: %APP_NAME%-api
echo     app.kubernetes.io/part-of: %APP_NAME%
echo spec:
echo   to:
echo     kind: Service
echo     name: %APP_NAME%-api-service
echo   port:
echo     targetPort: %API_PORT%
echo   tls:
echo     termination: edge
echo     insecureEdgeTerminationPolicy: Redirect
) | oc apply -f -

@REM === שלב 6: הצגת התוצאות ===
echo.
echo ================================================================
echo                    DEPLOYMENT SUCCESSFUL
echo ================================================================
for /f "tokens=*" %%g in ('oc get route %APP_NAME%-api-route -o jsonpath="{.spec.host}"') do set "ROUTE_URL=%%g"
echo Project: %PROJECT_NAME%
echo App Name: %APP_NAME%
echo Deployment Type: %DEPLOYMENT_TYPE%
echo Application URL: https://!ROUTE_URL!
echo API Endpoint: https://!ROUTE_URL!/soldiersdb/
echo API Docs: https://!ROUTE_URL!/docs
echo Health Check: https://!ROUTE_URL!/health
echo ================================================================

endlocal
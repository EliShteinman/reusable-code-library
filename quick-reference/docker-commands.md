
```markdown
# Docker Commands Quick Reference

## Basic Commands
```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -p 8080:8080 myapp:latest

# List images
docker images

# List containers
docker ps -a

# Remove container
docker rm container_id

# Remove image
docker rmi image_id
```

## Multi-platform Build
```bash
# Setup buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest --push .
```

## Cleanup
```bash
# Remove unused images
docker image prune

# Remove all stopped containers
docker container prune

# Complete cleanup
docker system prune -a
```
```

### 4. `quick-reference/kubectl-cheatsheet.md`
```markdown
# Kubernetes/OpenShift Commands Cheat Sheet

## Basic Operations
```bash
# Get resources
oc get pods
oc get services
oc get deployments

# Describe resource
oc describe pod pod-name

# View logs
oc logs pod-name
oc logs -f deployment/app-name

# Execute commands in pod
oc exec -it pod-name -- /bin/bash
```

## Deployment
```bash
# Apply YAML
oc apply -f deployment.yaml

# Scale deployment
oc scale deployment app-name --replicas=3

# Rolling update
oc rollout restart deployment/app-name

# Check rollout status
oc rollout status deployment/app-name
```

## Troubleshooting
```bash
# Pod events
oc get events --sort-by=.metadata.creationTimestamp

# Resource usage
oc top pods
oc top nodes

# Port forward
oc port-forward pod/app-pod 8080:8080
```
```

### 5. `quick-reference/troubleshooting.md`
```markdown
# Common Issues and Solutions

## Docker Issues

### Build Fails
```bash
# Clear cache
docker builder prune

# Build without cache
docker build --no-cache -t myapp .
```

### Permission Denied
```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

## Kubernetes/OpenShift Issues

### Pod Stuck in Pending
```bash
# Check node resources
oc describe nodes

# Check PVC status
oc get pvc

# Check events
oc get events --sort-by=.metadata.creationTimestamp
```

### Service Not Accessible
```bash
# Check service endpoints
oc get endpoints service-name

# Test internal connectivity
oc run test-pod --image=busybox --rm -it -- nslookup service-name
```

### Database Connection Issues
```bash
# Check if database pod is ready
oc get pods -l app=database

# Test database connectivity
oc exec -it database-pod -- mysql -u user -p -e "SELECT 1;"

# Check database logs
oc logs -l app=database
```

## Python/FastAPI Issues

### Import Errors
```bash
# Check installed packages
pip list

# Install missing packages
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 PID
```
```

### 6. `configuration-templates/environment/.env-template`
```bash
# configuration-templates/environment/.env-template
# Environment variables template for applications

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword

# MongoDB Configuration (alternative)
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB_NAME=mydatabase
MONGO_USER=mongouser
MONGO_PASSWORD=mongopassword

# Application Configuration
APP_PORT=8080
LOG_LEVEL=INFO
DEBUG=false

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET=your-jwt-secret-change-in-production

# External APIs
API_KEY=your-api-key
API_URL=https://api.example.com

# Redis (if needed)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Email (if needed)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
```

### 7. `configuration-templates/environment/docker-compose.yml-template`
```yaml
# configuration-templates/environment/docker-compose.yml-template
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=database
      - DB_PORT=3306
      - DB_NAME=mydatabase
      - DB_USER=myuser
      - DB_PASSWORD=mypassword
    depends_on:
      - database
    volumes:
      - ./logs:/app/logs

  database:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=mydatabase
      - MYSQL_USER=myuser
      - MYSQL_PASSWORD=mypassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  # Alternative: MongoDB
  # mongodb:
  #   image: mongo:7.0
  #   environment:
  #     - MONGO_INITDB_ROOT_USERNAME=mongoadmin
  #     - MONGO_INITDB_ROOT_PASSWORD=mongopassword
  #     - MONGO_INITDB_DATABASE=mydatabase
  #   ports:
  #     - "27017:27017"
  #   volumes:
  #     - mongodb_data:/data/db

  # Optional: Redis
  # redis:
  #   image: redis:7.0-alpine
  #   ports:
  #     - "6379:6379"
  #   volumes:
  #     - redis_data:/data

volumes:
  mysql_data:
  # mongodb_data:
  # redis_data:
```

---


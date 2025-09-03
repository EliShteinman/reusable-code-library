# docker-templates/python-fastapi/Dockerfile
# Template Dockerfile for FastAPI applications
# Customize paths and requirements as needed

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Customize the source path based on your project structure
COPY ./services /app/services

# Expose the application port
# Change port number as needed
EXPOSE 8080

# Command to run the application
# Customize the module path based on your project structure
CMD ["uvicorn", "services.data_loader.main:app", "--host", "0.0.0.0", "--port", "8080"]
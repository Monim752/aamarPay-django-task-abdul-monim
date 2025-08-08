# Use Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app/aamarpay_project

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . /app/

# Expose port
EXPOSE 8000

# Default command (overridden in docker-compose.yml)
CMD ["gunicorn", "aamarpay_project.wsgi:application", "--bind", "0.0.0.0:8000"]

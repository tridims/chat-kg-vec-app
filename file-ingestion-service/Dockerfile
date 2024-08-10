# Stage 1: Build dependencies
FROM python:3.12-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Set up working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY src ./src
COPY app.py ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Stage 2: Run the application
FROM python:3.12-slim

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set up working directory
WORKDIR /app

# Copy application files
COPY --from=builder /app /app

# Create temp_storage directory
RUN mkdir -p /app/temp_storage

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
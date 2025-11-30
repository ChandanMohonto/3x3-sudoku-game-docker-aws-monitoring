# Dockerfile for Sudoku Game
# Multi-stage build for optimized image size

# Stage 1: Base image with Python
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements file
COPY requirements.txt .

# Install dependencies (if any)
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final image
FROM base as final

# Copy dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY app.py .
COPY sudoku_game.py .
COPY templates/ ./templates/

# Make the scripts executable
RUN chmod +x app.py sudoku_game.py

# Add metadata labels
LABEL maintainer="your-email@example.com" \
      description="Interactive Sudoku Puzzle Game - Web Version" \
      version="2.0"

# Expose port for web interface
EXPOSE 5000

# Set the entrypoint to run Flask app
ENTRYPOINT ["python3", "app.py"]

# Default command
CMD []

# A2A Indian University Library Federation - Dockerfile
# ======================================================
# Single Dockerfile that can run any of the agents
# Usage: docker build --build-arg AGENT=iit_delhi_library_agent -t iit-delhi .

FROM python:3.11-slim

# Build argument to specify which agent to run
ARG AGENT=iit_delhi_library_agent
ENV AGENT=${AGENT}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports (will be overridden in docker-compose)
EXPOSE 8000 8003 8004

# Default command - run the specified agent
CMD python -m ${AGENT}.agent

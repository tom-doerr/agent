FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the web_dspy_builder module
COPY . /app/web_dspy_builder/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DSPY_BUILDER_HOST=0.0.0.0
ENV DSPY_BUILDER_PORT=8800

# Expose the port
EXPOSE 8800

# Run the application
CMD ["python", "-m", "web_dspy_builder"]
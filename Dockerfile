FROM python:3.11-slim

WORKDIR /app

# Copy source code and config first (needed for non-editable install)
COPY pyproject.toml ./
COPY src ./src

# Install dependencies
RUN pip install --no-cache-dir .

# Expose port
EXPOSE 8000

# Run the API
CMD ["python", "-m", "uvicorn", "komikan.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

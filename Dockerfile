# Build stage: Install dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry==1.8.5

# Copy dependency files
COPY pyproject.toml ./

# Export and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry export -f requirements.txt --output requirements.txt --without-hashes \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage: Distroless
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /install/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy application code
COPY src/hello_world ./hello_world

# Expose port
EXPOSE 8000

# Run as non-root
USER nonroot

# Run the application
CMD ["python", "-m", "hello_world.main"]

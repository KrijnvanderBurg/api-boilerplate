# =============================================================================
# Build stage: Install dependencies
# =============================================================================
FROM python:3.13-slim AS python-base

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry==1.8.5

# Copy dependency files
COPY pyproject.toml ./

# Export and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry export -f requirements.txt --output requirements.txt --without-hashes \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# =============================================================================
# Runtime stage: Custom distroless with Python 3.13
# =============================================================================
FROM gcr.io/distroless/cc-debian13

WORKDIR /app

# Copy Python 3.13 runtime from python-base
COPY --from=python-base /usr/local/bin/python3.13 /usr/local/bin/python3.13
COPY --from=python-base /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=python-base /usr/local/lib/libpython3.13.so.1.0 /usr/local/lib/libpython3.13.so.1.0

# Copy installed packages
COPY --from=python-base /install/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy application code
COPY src/hello_world ./hello_world

# Expose port
EXPOSE 8000

# Run as non-root
USER nonroot

# Run the application
ENTRYPOINT ["/usr/local/bin/python3.13"]
CMD ["-m", "hello_world.main"]

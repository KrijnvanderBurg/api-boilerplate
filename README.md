API Boilerplate

## Development

```bash
.github/scripts/poetry-install.sh    # Install dependencies
.github/scripts/run-pytest.sh        # Run tests
```

## Running with OpenTelemetry

```bash
# Run with instrumentation (sends traces to Tempo)
OTEL_SERVICE_NAME=hello-world-api \
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318 \
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf \
OTEL_TRACES_EXPORTER=otlp \
OTEL_METRICS_EXPORTER=none \
OTEL_LOGS_EXPORTER=none \
opentelemetry-instrument python -m hello_world
```

Generate traffic:
```bash
for i in {1..100}; do
  curl http://localhost:8000/health
  curl http://localhost:8000/items
  curl http://localhost:8000/items/1
  sleep 0.1
done
```

View in Grafana: http://localhost:3000
- Go to Explore → Tempo
- Search for traces with: `{service.name="hello-world-api"}`
- Or open the "FastAPI Observability" dashboard


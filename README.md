API Boilerplate

## Development

```bash
.github/scripts/poetry-install.sh    # Install dependencies
.github/scripts/run-pytest.sh        # Run tests
```

## Running with OpenTelemetry

```bash
# Run with instrumentation (sends traces to Tempo)
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318 \
OTEL_TRACES_EXPORTER=otlp \
opentelemetry-instrument python -m hello_world
```

Then make some requests:
```bash
# Generate traffic to see metrics in Grafana
for i in {1..100}; do
  curl http://localhost:8000/health
  curl http://localhost:8000/items
  curl http://localhost:8000/items/1
  sleep 0.1
done
```

View traces and metrics in Grafana: http://localhost:3000
- Dashboard: "FastAPI Observability"


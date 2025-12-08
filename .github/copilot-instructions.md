# Hello World
TODO

## Development environment
All dependencies and tool configurations are defined in `pyproject.toml`. Poetry virtualenv is disabled - dependencies are installed directly:

```bash
.github/scripts/poetry-install.sh    # Install dependencies
```

## Running tests
```bash
.github/scripts/run-pytest.sh        # Run all tests with coverage
```

## Running pipelines
Execute a pipeline with configuration files:

```bash
python -m hello_world run \
  --alert-filepath examples/yaml_products_cleanup/alert.yaml \
  --workflow-filepath examples/yaml_products_cleanup/job.yaml
```

Validate configurations without running:

```bash
python -m hello_world validate \
  --alert-filepath <path> \
  --workflow-filepath <path>
```

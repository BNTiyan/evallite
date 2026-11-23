# evallite

Lightning-Fast, Local-First Agent & Tool-Call Evaluation Engine with Interactive Terminal Dashboard.

## Highlights

- **Local-First Execution**: Run evaluations locally with $0.00 cloud API costs.
- **Tool-Call & Schema Verification**: Validate tool selection, required parameters, and types.
- **Hallucination Detection**: Catch unexpected arguments injected by LLMs outside the schema.
- **Interactive Terminal Dashboard**: Real-time evaluation matrix, argument diff visualizer, and latency metrics.
- **CI/CD Integration**: Enforce accuracy SLAs in continuous integration pipelines with `--ci`.

## Quick Start

```bash
pip install -e .

# Run the built-in interactive demonstration suite
evallite demo

# Run in CI mode (fails with exit code 1 if accuracy drops below threshold)
evallite demo --ci

# Run evaluation suite from a JSON file
evallite run suite.json --min-accuracy 95 --ci
```

## Suite Format

Define evaluation cases in JSON or YAML:

```json
[
  {
    "id": "weather-check",
    "prompt": "What is the temperature in Paris in Celsius?",
    "expected_tool": "get_weather",
    "expected_args": {
      "city": "Paris",
      "units": "celsius"
    },
    "forbidden_args": ["auth_token"],
    "assertions": ["contains:Paris"],
    "max_latency_ms": 500.0
  }
]
```

## Running Tests

```bash
pytest tests/ -v
```

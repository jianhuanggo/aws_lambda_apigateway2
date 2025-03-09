# AWS Lambda API Gateway Integration

A Python package to create API Gateway endpoints that trigger AWS Lambda functions.

## Features

- Create API Gateway endpoints that trigger Lambda functions
- Support for multiple AWS profiles, including a special 'latest' profile
- Command-line interface for easy management
- Comprehensive Python API for programmatic usage
- Production-grade code with full test coverage

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Create an API Gateway endpoint for a Lambda function
python -m aws_lambda_apigateway.cli.main create-api --api-name MyAPI --lambda-name MyFunction --profile default

# Use 'latest' profile
python -m aws_lambda_apigateway.cli.main create-api --api-name MyAPI --lambda-name MyFunction --profile latest
```

## Documentation

See [USAGE.md](USAGE.md) for detailed documentation.

## Examples

See the [examples](aws_lambda_apigateway/examples) directory for usage examples.

## Development

### Setup

```bash
pip install -e .
pip install -r requirements-dev.txt
```

### Running Tests

```bash
python -m pytest
```

## License

MIT

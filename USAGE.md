# AWS Lambda API Gateway Integration

This package provides a simple way to create and manage API Gateway endpoints that trigger AWS Lambda functions.

## Installation

```bash
pip install -e .
```

## Command Line Usage

The package provides a command-line interface for creating and managing API Gateway endpoints.

### Creating an API Gateway Endpoint

```bash
# Create an API Gateway endpoint for a Lambda function
python -m aws_lambda_apigateway.cli.main create-api --api-name MyAPI --lambda-name MyFunction --profile default

# Use 'latest' profile (uses the latest AWS credentials)
python -m aws_lambda_apigateway.cli.main create-api --api-name MyAPI --lambda-name MyFunction --profile latest

# Specify a region
python -m aws_lambda_apigateway.cli.main create-api --api-name MyAPI --lambda-name MyFunction --region us-west-2

# Add a description
python -m aws_lambda_apigateway.cli.main create-api --api-name MyAPI --lambda-name MyFunction --description "My API Gateway"

# Get JSON output
python -m aws_lambda_apigateway.cli.main create-api --api-name MyAPI --lambda-name MyFunction --output json
```

### Deleting an API Gateway

```bash
python -m aws_lambda_apigateway.cli.main delete-api --api-id abc123
```

### Listing API Gateways

```bash
python -m aws_lambda_apigateway.cli.main list-apis
```

### Getting API Gateway Details

```bash
python -m aws_lambda_apigateway.cli.main get-api --api-id abc123
```

### Test Invoking an API Gateway Endpoint

```bash
python -m aws_lambda_apigateway.cli.main test-invoke --api-id abc123 --resource-path /my-lambda --http-method POST --body '{"key": "value"}'
```

### Working with AWS Profiles

```bash
# List available AWS profiles
python -m aws_lambda_apigateway.cli.main list-profiles

# Get information about a profile
python -m aws_lambda_apigateway.cli.main get-profile-info --profile default
```

## Python API Usage

You can also use the package programmatically in your Python code.

```python
from aws_lambda_apigateway.core.api_gateway import APIGatewayLambdaIntegration

# Create an API Gateway Lambda integration
integration = APIGatewayLambdaIntegration(profile_name='default', region_name='us-east-1')

# Create an API Gateway endpoint for a Lambda function
result = integration.create_api('MyAPI', 'MyFunction', 'My API Gateway')
print(f"API Gateway created: {result['api_id']}")
print(f"Invoke URL: {result['invoke_url']}")

# List API Gateways
apis = integration.list_apis()
for api in apis:
    print(f"API: {api['name']} (ID: {api['id']})")

# Delete an API Gateway
integration.delete_api('abc123')
```

## AWS Profile Support

The package supports multiple AWS profiles, including a special 'latest' profile that uses the latest AWS credentials.

```python
# Use default profile
integration = APIGatewayLambdaIntegration()

# Use a specific profile
integration = APIGatewayLambdaIntegration(profile_name='dev')

# Use latest credentials
integration = APIGatewayLambdaIntegration(profile_name='latest')

# Specify a region
integration = APIGatewayLambdaIntegration(profile_name='prod', region_name='us-west-2')
```

## Example Script

See the `examples/sample_usage.py` script for a complete example of using the package.

```bash
python -m aws_lambda_apigateway.examples.sample_usage
```

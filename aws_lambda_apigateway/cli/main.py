"""
Command-line interface for AWS Lambda API Gateway integration.
"""
import json
import logging
import sys
from typing import Optional

import click

from aws_lambda_apigateway.core.api_gateway import APIGatewayLambdaIntegration
from aws_lambda_apigateway.core.profile_manager import ProfileManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

@click.group()
@click.version_option()
def cli():
    """
    AWS Lambda API Gateway Integration CLI.
    
    Create and manage API Gateway endpoints that trigger Lambda functions.
    """
    pass

@cli.command('create-api')
@click.option('--api-name', required=True, help='Name of the API Gateway to create')
@click.option('--lambda-name', required=True, help='Name of the Lambda function to integrate with')
@click.option('--description', default='', help='Description of the API Gateway')
@click.option('--profile', default=None, help='AWS profile to use. Use "latest" for latest credentials')
@click.option('--region', default=None, help='AWS region to use')
@click.option('--output', type=click.Choice(['json', 'text']), default='text', help='Output format')
def create_api(api_name: str, lambda_name: str, description: str, profile: Optional[str], 
              region: Optional[str], output: str):
    """
    Create an API Gateway endpoint that triggers a Lambda function.
    """
    try:
        integration = APIGatewayLambdaIntegration(profile_name=profile, region_name=region)
        result = integration.create_api(api_name, lambda_name, description)
        
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"API Gateway created successfully!")
            click.echo(f"API ID: {result['api_id']}")
            click.echo(f"API Name: {result['api_name']}")
            click.echo(f"Lambda Function: {result['lambda_name']}")
            click.echo(f"Lambda ARN: {result['lambda_arn']}")
            click.echo(f"Invoke URL: {result['invoke_url']}")
            click.echo(f"Stage: {result['stage']}")
    except Exception as e:
        logger.error(f"Error creating API Gateway: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('delete-api')
@click.option('--api-id', required=True, help='ID of the API Gateway to delete')
@click.option('--profile', default=None, help='AWS profile to use. Use "latest" for latest credentials')
@click.option('--region', default=None, help='AWS region to use')
@click.option('--output', type=click.Choice(['json', 'text']), default='text', help='Output format')
def delete_api(api_id: str, profile: Optional[str], region: Optional[str], output: str):
    """
    Delete an API Gateway.
    """
    try:
        integration = APIGatewayLambdaIntegration(profile_name=profile, region_name=region)
        result = integration.delete_api(api_id)
        
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"API Gateway {api_id} deleted successfully!")
    except Exception as e:
        logger.error(f"Error deleting API Gateway: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('list-apis')
@click.option('--profile', default=None, help='AWS profile to use. Use "latest" for latest credentials')
@click.option('--region', default=None, help='AWS region to use')
@click.option('--output', type=click.Choice(['json', 'text']), default='text', help='Output format')
def list_apis(profile: Optional[str], region: Optional[str], output: str):
    """
    List all API Gateways.
    """
    try:
        integration = APIGatewayLambdaIntegration(profile_name=profile, region_name=region)
        apis = integration.list_apis()
        
        if output == 'json':
            click.echo(json.dumps(apis, indent=2))
        else:
            if not apis:
                click.echo("No API Gateways found.")
                return
                
            click.echo("API Gateways:")
            for api in apis:
                click.echo(f"  ID: {api['id']}")
                click.echo(f"  Name: {api['name']}")
                click.echo(f"  Created: {api['createdDate']}")
                click.echo("")
    except Exception as e:
        logger.error(f"Error listing API Gateways: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('get-api')
@click.option('--api-id', required=True, help='ID of the API Gateway')
@click.option('--profile', default=None, help='AWS profile to use. Use "latest" for latest credentials')
@click.option('--region', default=None, help='AWS region to use')
@click.option('--output', type=click.Choice(['json', 'text']), default='text', help='Output format')
def get_api(api_id: str, profile: Optional[str], region: Optional[str], output: str):
    """
    Get details of an API Gateway.
    """
    try:
        integration = APIGatewayLambdaIntegration(profile_name=profile, region_name=region)
        api = integration.get_api(api_id)
        
        if output == 'json':
            click.echo(json.dumps(api, indent=2))
        else:
            click.echo(f"API Gateway Details:")
            click.echo(f"  ID: {api['id']}")
            click.echo(f"  Name: {api['name']}")
            click.echo(f"  Description: {api.get('description', 'N/A')}")
            click.echo(f"  Created: {api['createdDate']}")
            click.echo(f"  API Key Source: {api.get('apiKeySource', 'N/A')}")
            click.echo(f"  Endpoint Configuration: {api.get('endpointConfiguration', {}).get('types', ['N/A'])}")
    except Exception as e:
        logger.error(f"Error getting API Gateway details: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('test-invoke')
@click.option('--api-id', required=True, help='ID of the API Gateway')
@click.option('--resource-path', required=True, help='Path of the resource to invoke')
@click.option('--http-method', default='POST', help='HTTP method to use')
@click.option('--body', default='{}', help='Request body as JSON string')
@click.option('--profile', default=None, help='AWS profile to use. Use "latest" for latest credentials')
@click.option('--region', default=None, help='AWS region to use')
@click.option('--output', type=click.Choice(['json', 'text']), default='text', help='Output format')
def test_invoke(api_id: str, resource_path: str, http_method: str, body: str, 
               profile: Optional[str], region: Optional[str], output: str):
    """
    Test invoke an API Gateway endpoint.
    """
    try:
        integration = APIGatewayLambdaIntegration(profile_name=profile, region_name=region)
        result = integration.test_invoke_api(api_id, resource_path, http_method, body)
        
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Test Invoke Result:")
            click.echo(f"  Status: {result['status']}")
            click.echo(f"  Status Code: {result.get('statusCode', 'N/A')}")
            click.echo(f"  Response Body: {result.get('body', 'N/A')}")
    except Exception as e:
        logger.error(f"Error test invoking API Gateway: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('list-profiles')
@click.option('--output', type=click.Choice(['json', 'text']), default='text', help='Output format')
def list_profiles(output: str):
    """
    List all available AWS profiles.
    """
    try:
        profiles = ProfileManager.list_profiles()
        
        if output == 'json':
            click.echo(json.dumps(profiles, indent=2))
        else:
            if not profiles:
                click.echo("No AWS profiles found.")
                return
                
            click.echo("AWS Profiles:")
            for profile in profiles:
                click.echo(f"  {profile}")
    except Exception as e:
        logger.error(f"Error listing AWS profiles: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('get-profile-info')
@click.option('--profile', default=None, help='AWS profile to get info for')
@click.option('--output', type=click.Choice(['json', 'text']), default='text', help='Output format')
def get_profile_info(profile: Optional[str], output: str):
    """
    Get information about an AWS profile.
    """
    try:
        info = ProfileManager.get_profile_info(profile)
        
        if output == 'json':
            click.echo(json.dumps(info, indent=2))
        else:
            click.echo(f"Profile Information:")
            click.echo(f"  Profile: {info['profile']}")
            click.echo(f"  Account ID: {info['account_id']}")
            click.echo(f"  User ID: {info['user_id']}")
            click.echo(f"  ARN: {info['arn']}")
            click.echo(f"  Region: {info['region']}")
    except Exception as e:
        logger.error(f"Error getting profile info: {e}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()

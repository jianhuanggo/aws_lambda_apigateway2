"""
Sample usage of the AWS Lambda API Gateway integration.
"""
import json
import logging
import os
import sys
import time
from typing import Dict, Any

# Add parent directory to path to allow importing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from aws_lambda_apigateway.core.api_gateway import APIGatewayLambdaIntegration
from aws_lambda_apigateway.core.profile_manager import ProfileManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def print_section(title: str):
    """Print a section title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_json(data: Dict[str, Any]):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))

def main():
    """
    Sample usage of the AWS Lambda API Gateway integration.
    """
    # Set your AWS profile and region
    profile_name = 'default'  # Use 'latest' for latest credentials
    region_name = 'us-east-1'
    
    # Set your API Gateway and Lambda function names
    api_name = f'SampleAPI-{int(time.time())}'
    lambda_name = 'YourLambdaFunctionName'  # Replace with your Lambda function name
    
    print_section("AWS Profile Information")
    
    # List available AWS profiles
    print("Available AWS profiles:")
    profiles = ProfileManager.list_profiles()
    for profile in profiles:
        print(f"  - {profile}")
    
    # Get information about the current profile
    print("\nCurrent profile information:")
    try:
        profile_info = ProfileManager.get_profile_info(profile_name)
        print_json(profile_info)
    except Exception as e:
        logger.error(f"Error getting profile info: {e}")
        print(f"Error: {str(e)}")
    
    print_section("Creating API Gateway")
    
    # Create API Gateway Lambda integration
    integration = APIGatewayLambdaIntegration(profile_name=profile_name, region_name=region_name)
    
    # List existing APIs
    print("Existing API Gateways:")
    try:
        apis = integration.list_apis()
        if not apis:
            print("  No API Gateways found.")
        else:
            for api in apis:
                print(f"  - {api['name']} (ID: {api['id']})")
    except Exception as e:
        logger.error(f"Error listing API Gateways: {e}")
        print(f"Error: {str(e)}")
    
    # Create API Gateway for Lambda function
    print(f"\nCreating API Gateway '{api_name}' for Lambda function '{lambda_name}'...")
    try:
        result = integration.create_api(api_name, lambda_name, f"Sample API for {lambda_name}")
        print("\nAPI Gateway created successfully!")
        print_json(result)
        
        api_id = result['api_id']
        invoke_url = result['invoke_url']
        
        print_section("API Gateway Details")
        
        # Get API Gateway details
        print(f"Getting details for API Gateway '{api_id}'...")
        api_details = integration.get_api(api_id)
        print_json(api_details)
        
        print_section("Testing API Gateway")
        
        # Test invoke the API Gateway
        print(f"Test invoking API Gateway '{api_id}'...")
        try:
            test_result = integration.test_invoke_api(
                api_id, 
                f"/{lambda_name}", 
                'POST', 
                json.dumps({"key": "value"})
            )
            print("\nTest invoke result:")
            print_json(test_result)
        except Exception as e:
            logger.error(f"Error test invoking API Gateway: {e}")
            print(f"Error: {str(e)}")
        
        print_section("Cleaning Up")
        
        # Delete the API Gateway
        print(f"Deleting API Gateway '{api_id}'...")
        delete_result = integration.delete_api(api_id)
        print("\nAPI Gateway deleted successfully!")
        print_json(delete_result)
        
    except Exception as e:
        logger.error(f"Error in sample usage: {e}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

"""
Core functionality for creating and managing API Gateway endpoints for Lambda functions.
"""
import logging
import time
from typing import Dict, List, Optional, Any, Union

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class APIGatewayLambdaIntegration:
    """
    Class to create and manage API Gateway endpoints that trigger Lambda functions.
    """
    
    def __init__(self, profile_name: Optional[str] = None, region_name: Optional[str] = None):
        """
        Initialize the API Gateway Lambda Integration.
        
        Args:
            profile_name: AWS profile name to use. If 'latest', uses the latest credentials.
            region_name: AWS region name to use. If None, uses the default region.
        """
        self.profile_name = profile_name
        self.region_name = region_name
        self.session = self._create_session()
        self.apigateway_client = self.session.client('apigateway')
        self.lambda_client = self.session.client('lambda')
        
    def _create_session(self) -> boto3.Session:
        """
        Create a boto3 session with the specified profile and region.
        
        Returns:
            boto3.Session: The created session.
        """
        if self.profile_name == 'latest':
            # Use default session with latest credentials
            logger.info("Using latest AWS credentials")
            return boto3.Session(region_name=self.region_name)
        else:
            logger.info(f"Using AWS profile: {self.profile_name}")
            return boto3.Session(profile_name=self.profile_name, region_name=self.region_name)
    
    def create_api(self, api_name: str, lambda_name: str, description: str = "") -> Dict[str, Any]:
        """
        Create an API Gateway endpoint that triggers a Lambda function.
        
        Args:
            api_name: Name of the API Gateway to create.
            lambda_name: Name of the Lambda function to integrate with.
            description: Description of the API Gateway.
            
        Returns:
            Dict containing the API Gateway details including the invoke URL.
        """
        try:
            # Check if Lambda function exists
            lambda_function = self._get_lambda_function(lambda_name)
            if not lambda_function:
                raise ValueError(f"Lambda function '{lambda_name}' not found")
            
            # Create REST API
            logger.info(f"Creating API Gateway: {api_name}")
            api = self.apigateway_client.create_rest_api(
                name=api_name,
                description=description,
                endpointConfiguration={'types': ['REGIONAL']}
            )
            api_id = api['id']
            
            # Get the root resource ID
            resources = self.apigateway_client.get_resources(restApiId=api_id)
            root_id = [resource['id'] for resource in resources['items'] 
                      if resource['path'] == '/'][0]
            
            # Create a resource
            resource = self.apigateway_client.create_resource(
                restApiId=api_id,
                parentId=root_id,
                pathPart=lambda_name
            )
            resource_id = resource['id']
            
            # Create a method
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                authorizationType='NONE'
            )
            
            # Set up Lambda integration
            lambda_arn = lambda_function['Configuration']['FunctionArn']
            region = self.session.region_name
            account_id = lambda_arn.split(':')[4]
            
            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                type='AWS',
                integrationHttpMethod='POST',
                uri=f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
            )
            
            # Set up method response
            self.apigateway_client.put_method_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                statusCode='200',
                responseModels={'application/json': 'Empty'}
            )
            
            # Set up integration response
            self.apigateway_client.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                statusCode='200',
                responseTemplates={'application/json': ''}
            )
            
            # Add Lambda permission
            source_arn = f'arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*/{lambda_name}'
            self._add_lambda_permission(lambda_name, source_arn)
            
            # Deploy the API
            deployment = self.apigateway_client.create_deployment(
                restApiId=api_id,
                stageName='prod'
            )
            
            # Get the invoke URL
            invoke_url = f'https://{api_id}.execute-api.{region}.amazonaws.com/prod/{lambda_name}'
            
            return {
                'api_id': api_id,
                'api_name': api_name,
                'lambda_name': lambda_name,
                'lambda_arn': lambda_arn,
                'invoke_url': invoke_url,
                'deployment_id': deployment['id'],
                'stage': 'prod'
            }
            
        except ClientError as e:
            logger.error(f"Error creating API Gateway: {e}")
            raise
    
    def delete_api(self, api_id: str) -> Dict[str, Any]:
        """
        Delete an API Gateway.
        
        Args:
            api_id: ID of the API Gateway to delete.
            
        Returns:
            Dict containing the result of the deletion.
        """
        try:
            logger.info(f"Deleting API Gateway: {api_id}")
            response = self.apigateway_client.delete_rest_api(restApiId=api_id)
            return {'status': 'deleted', 'api_id': api_id}
        except ClientError as e:
            logger.error(f"Error deleting API Gateway: {e}")
            raise
    
    def list_apis(self) -> List[Dict[str, Any]]:
        """
        List all API Gateways.
        
        Returns:
            List of API Gateway details.
        """
        try:
            logger.info("Listing API Gateways")
            response = self.apigateway_client.get_rest_apis()
            return response['items']
        except ClientError as e:
            logger.error(f"Error listing API Gateways: {e}")
            raise
    
    def get_api(self, api_id: str) -> Dict[str, Any]:
        """
        Get details of an API Gateway.
        
        Args:
            api_id: ID of the API Gateway.
            
        Returns:
            Dict containing the API Gateway details.
        """
        try:
            logger.info(f"Getting API Gateway: {api_id}")
            response = self.apigateway_client.get_rest_api(restApiId=api_id)
            return response
        except ClientError as e:
            logger.error(f"Error getting API Gateway: {e}")
            raise
    
    def _get_lambda_function(self, lambda_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a Lambda function.
        
        Args:
            lambda_name: Name of the Lambda function.
            
        Returns:
            Dict containing the Lambda function details or None if not found.
        """
        try:
            logger.info(f"Getting Lambda function: {lambda_name}")
            response = self.lambda_client.get_function(FunctionName=lambda_name)
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning(f"Lambda function not found: {lambda_name}")
                return None
            logger.error(f"Error getting Lambda function: {e}")
            raise
    
    def _add_lambda_permission(self, lambda_name: str, source_arn: str) -> Dict[str, Any]:
        """
        Add permission to a Lambda function to allow API Gateway to invoke it.
        
        Args:
            lambda_name: Name of the Lambda function.
            source_arn: ARN of the API Gateway resource.
            
        Returns:
            Dict containing the result of the operation.
        """
        try:
            logger.info(f"Adding Lambda permission for: {lambda_name}")
            statement_id = f'apigateway-{int(time.time())}'
            response = self.lambda_client.add_permission(
                FunctionName=lambda_name,
                StatementId=statement_id,
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=source_arn
            )
            return response
        except ClientError as e:
            logger.error(f"Error adding Lambda permission: {e}")
            raise
    
    def test_invoke_api(self, api_id: str, resource_path: str, 
                       http_method: str = 'POST', body: Optional[str] = None) -> Dict[str, Any]:
        """
        Test invoke an API Gateway endpoint.
        
        Args:
            api_id: ID of the API Gateway.
            resource_path: Path of the resource to invoke.
            http_method: HTTP method to use.
            body: Request body.
            
        Returns:
            Dict containing the response from the API Gateway.
        """
        try:
            logger.info(f"Test invoking API Gateway: {api_id}, path: {resource_path}")
            response = self.apigateway_client.test_invoke_method(
                restApiId=api_id,
                resourceId=self._get_resource_id(api_id, resource_path),
                httpMethod=http_method,
                body=body or '{}'
            )
            return response
        except ClientError as e:
            logger.error(f"Error test invoking API Gateway: {e}")
            raise
    
    def _get_resource_id(self, api_id: str, resource_path: str) -> str:
        """
        Get the ID of a resource in an API Gateway.
        
        Args:
            api_id: ID of the API Gateway.
            resource_path: Path of the resource.
            
        Returns:
            ID of the resource.
        """
        try:
            resources = self.apigateway_client.get_resources(restApiId=api_id)
            for resource in resources['items']:
                if resource['path'] == resource_path:
                    return resource['id']
            raise ValueError(f"Resource not found: {resource_path}")
        except ClientError as e:
            logger.error(f"Error getting resource ID: {e}")
            raise

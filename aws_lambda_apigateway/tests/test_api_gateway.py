"""
Unit tests for the API Gateway Lambda integration.
"""
import json
import unittest
from unittest.mock import patch, MagicMock

import boto3
import pytest
from botocore.exceptions import ClientError

from aws_lambda_apigateway.core.api_gateway import APIGatewayLambdaIntegration

class TestAPIGatewayLambdaIntegration:
    """
    Test cases for the APIGatewayLambdaIntegration class.
    """
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock boto3 session."""
        with patch('boto3.Session') as mock:
            mock_session = MagicMock()
            mock.return_value = mock_session
            
            # Mock clients
            mock_apigateway = MagicMock()
            mock_lambda = MagicMock()
            
            mock_session.client.side_effect = lambda service, **kwargs: {
                'apigateway': mock_apigateway,
                'lambda': mock_lambda
            }.get(service)
            
            # Store mocks for assertions
            mock_session.mock_apigateway = mock_apigateway
            mock_session.mock_lambda = mock_lambda
            
            yield mock_session
    
    @pytest.fixture
    def integration(self, mock_session):
        """Create an APIGatewayLambdaIntegration instance with mocked session."""
        with patch.object(APIGatewayLambdaIntegration, '_create_session', return_value=mock_session):
            integration = APIGatewayLambdaIntegration(profile_name='test-profile', region_name='us-east-1')
            integration.apigateway_client = mock_session.mock_apigateway
            integration.lambda_client = mock_session.mock_lambda
            yield integration
    
    def test_init(self, mock_session):
        """Test initialization of APIGatewayLambdaIntegration."""
        # Test with profile name
        integration = APIGatewayLambdaIntegration(profile_name='test-profile', region_name='us-east-1')
        assert integration.profile_name == 'test-profile'
        assert integration.region_name == 'us-east-1'
        
        # Test with 'latest' profile
        integration = APIGatewayLambdaIntegration(profile_name='latest', region_name='us-west-2')
        assert integration.profile_name == 'latest'
        assert integration.region_name == 'us-west-2'
    
    def test_create_session(self):
        """Test session creation with different profile names."""
        with patch('boto3.Session') as mock_session:
            # Test with regular profile
            integration = APIGatewayLambdaIntegration(profile_name='test-profile', region_name='us-east-1')
            integration._create_session()
            mock_session.assert_called_with(profile_name='test-profile', region_name='us-east-1')
            
            # Test with 'latest' profile
            mock_session.reset_mock()
            integration = APIGatewayLambdaIntegration(profile_name='latest', region_name='us-west-2')
            integration._create_session()
            mock_session.assert_called_with(region_name='us-west-2')
    
    def test_create_api(self, integration, mock_session):
        """Test creating an API Gateway."""
        # Mock Lambda function response
        lambda_function = {
            'Configuration': {
                'FunctionName': 'test-lambda',
                'FunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:test-lambda'
            }
        }
        integration.lambda_client.get_function.return_value = lambda_function
        
        # Mock API Gateway responses
        mock_session.region_name = 'us-east-1'
        integration.apigateway_client.create_rest_api.return_value = {'id': 'api123'}
        integration.apigateway_client.get_resources.return_value = {
            'items': [{'id': 'root123', 'path': '/'}]
        }
        integration.apigateway_client.create_resource.return_value = {'id': 'resource123'}
        integration.apigateway_client.create_deployment.return_value = {'id': 'deployment123'}
        
        # Call the method
        result = integration.create_api('test-api', 'test-lambda', 'Test API')
        
        # Verify the result
        assert result['api_id'] == 'api123'
        assert result['api_name'] == 'test-api'
        assert result['lambda_name'] == 'test-lambda'
        assert result['lambda_arn'] == 'arn:aws:lambda:us-east-1:123456789012:function:test-lambda'
        assert result['invoke_url'] == 'https://api123.execute-api.us-east-1.amazonaws.com/prod/test-lambda'
        assert result['deployment_id'] == 'deployment123'
        assert result['stage'] == 'prod'
        
        # Verify API Gateway client calls
        integration.apigateway_client.create_rest_api.assert_called_with(
            name='test-api',
            description='Test API',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        integration.apigateway_client.get_resources.assert_called_with(restApiId='api123')
        integration.apigateway_client.create_resource.assert_called_with(
            restApiId='api123',
            parentId='root123',
            pathPart='test-lambda'
        )
        integration.apigateway_client.put_method.assert_called_with(
            restApiId='api123',
            resourceId='resource123',
            httpMethod='POST',
            authorizationType='NONE'
        )
        integration.apigateway_client.put_integration.assert_called_with(
            restApiId='api123',
            resourceId='resource123',
            httpMethod='POST',
            type='AWS',
            integrationHttpMethod='POST',
            uri='arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:test-lambda/invocations'
        )
        integration.apigateway_client.create_deployment.assert_called_with(
            restApiId='api123',
            stageName='prod'
        )
        
        # Verify Lambda client calls
        integration.lambda_client.get_function.assert_called_with(FunctionName='test-lambda')
        integration.lambda_client.add_permission.assert_called_once()
    
    def test_create_api_lambda_not_found(self, integration):
        """Test creating an API Gateway with non-existent Lambda function."""
        # Mock Lambda function not found
        integration.lambda_client.get_function.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Function not found'}},
            'GetFunction'
        )
        
        # Call the method and verify it raises ValueError
        with pytest.raises(ValueError, match="Lambda function 'test-lambda' not found"):
            integration.create_api('test-api', 'test-lambda', 'Test API')
    
    def test_delete_api(self, integration):
        """Test deleting an API Gateway."""
        # Mock API Gateway response
        integration.apigateway_client.delete_rest_api.return_value = {}
        
        # Call the method
        result = integration.delete_api('api123')
        
        # Verify the result
        assert result['status'] == 'deleted'
        assert result['api_id'] == 'api123'
        
        # Verify API Gateway client call
        integration.apigateway_client.delete_rest_api.assert_called_with(restApiId='api123')
    
    def test_list_apis(self, integration):
        """Test listing API Gateways."""
        # Mock API Gateway response
        apis = [
            {'id': 'api123', 'name': 'test-api-1', 'createdDate': '2023-01-01T00:00:00Z'},
            {'id': 'api456', 'name': 'test-api-2', 'createdDate': '2023-01-02T00:00:00Z'}
        ]
        integration.apigateway_client.get_rest_apis.return_value = {'items': apis}
        
        # Call the method
        result = integration.list_apis()
        
        # Verify the result
        assert result == apis
        
        # Verify API Gateway client call
        integration.apigateway_client.get_rest_apis.assert_called_once()
    
    def test_get_api(self, integration):
        """Test getting API Gateway details."""
        # Mock API Gateway response
        api = {
            'id': 'api123',
            'name': 'test-api',
            'description': 'Test API',
            'createdDate': '2023-01-01T00:00:00Z'
        }
        integration.apigateway_client.get_rest_api.return_value = api
        
        # Call the method
        result = integration.get_api('api123')
        
        # Verify the result
        assert result == api
        
        # Verify API Gateway client call
        integration.apigateway_client.get_rest_api.assert_called_with(restApiId='api123')
    
    def test_get_lambda_function(self, integration):
        """Test getting Lambda function details."""
        # Mock Lambda function response
        lambda_function = {
            'Configuration': {
                'FunctionName': 'test-lambda',
                'FunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:test-lambda'
            }
        }
        integration.lambda_client.get_function.return_value = lambda_function
        
        # Call the method
        result = integration._get_lambda_function('test-lambda')
        
        # Verify the result
        assert result == lambda_function
        
        # Verify Lambda client call
        integration.lambda_client.get_function.assert_called_with(FunctionName='test-lambda')
    
    def test_get_lambda_function_not_found(self, integration):
        """Test getting non-existent Lambda function."""
        # Mock Lambda function not found
        integration.lambda_client.get_function.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Function not found'}},
            'GetFunction'
        )
        
        # Call the method
        result = integration._get_lambda_function('test-lambda')
        
        # Verify the result
        assert result is None
        
        # Verify Lambda client call
        integration.lambda_client.get_function.assert_called_with(FunctionName='test-lambda')
    
    def test_add_lambda_permission(self, integration):
        """Test adding Lambda permission."""
        # Mock Lambda permission response
        permission = {
            'Statement': '{"Effect":"Allow","Action":"lambda:InvokeFunction"}'
        }
        integration.lambda_client.add_permission.return_value = permission
        
        # Call the method
        result = integration._add_lambda_permission(
            'test-lambda',
            'arn:aws:execute-api:us-east-1:123456789012:api123/*/*/test-lambda'
        )
        
        # Verify the result
        assert result == permission
        
        # Verify Lambda client call
        integration.lambda_client.add_permission.assert_called_once()
        args, kwargs = integration.lambda_client.add_permission.call_args
        assert kwargs['FunctionName'] == 'test-lambda'
        assert kwargs['Action'] == 'lambda:InvokeFunction'
        assert kwargs['Principal'] == 'apigateway.amazonaws.com'
        assert kwargs['SourceArn'] == 'arn:aws:execute-api:us-east-1:123456789012:api123/*/*/test-lambda'
    
    def test_test_invoke_api(self, integration):
        """Test invoking an API Gateway endpoint."""
        # Mock API Gateway responses
        resources = [
            {'id': 'resource123', 'path': '/test-lambda'}
        ]
        integration.apigateway_client.get_resources.return_value = {'items': resources}
        
        invoke_result = {
            'status': 200,
            'body': '{"result": "success"}'
        }
        integration.apigateway_client.test_invoke_method.return_value = invoke_result
        
        # Call the method
        result = integration.test_invoke_api(
            'api123',
            '/test-lambda',
            'POST',
            '{"key": "value"}'
        )
        
        # Verify the result
        assert result == invoke_result
        
        # Verify API Gateway client calls
        integration.apigateway_client.get_resources.assert_called_with(restApiId='api123')
        integration.apigateway_client.test_invoke_method.assert_called_with(
            restApiId='api123',
            resourceId='resource123',
            httpMethod='POST',
            body='{"key": "value"}'
        )
    
    def test_get_resource_id(self, integration):
        """Test getting resource ID."""
        # Mock API Gateway response
        resources = [
            {'id': 'root123', 'path': '/'},
            {'id': 'resource123', 'path': '/test-lambda'}
        ]
        integration.apigateway_client.get_resources.return_value = {'items': resources}
        
        # Call the method
        result = integration._get_resource_id('api123', '/test-lambda')
        
        # Verify the result
        assert result == 'resource123'
        
        # Verify API Gateway client call
        integration.apigateway_client.get_resources.assert_called_with(restApiId='api123')
    
    def test_get_resource_id_not_found(self, integration):
        """Test getting non-existent resource ID."""
        # Mock API Gateway response
        resources = [
            {'id': 'root123', 'path': '/'}
        ]
        integration.apigateway_client.get_resources.return_value = {'items': resources}
        
        # Call the method and verify it raises ValueError
        with pytest.raises(ValueError, match="Resource not found: /test-lambda"):
            integration._get_resource_id('api123', '/test-lambda')

"""
Unit tests for the CLI interface.
"""
import json
from unittest.mock import patch, MagicMock

import click
import pytest
from click.testing import CliRunner

from aws_lambda_apigateway.cli.main import cli, create_api, delete_api, list_apis, get_api, test_invoke, list_profiles, get_profile_info
from aws_lambda_apigateway.core.api_gateway import APIGatewayLambdaIntegration
from aws_lambda_apigateway.core.profile_manager import ProfileManager

class TestCLI:
    """
    Test cases for the CLI interface.
    """
    
    @pytest.fixture
    def runner(self):
        """Create a Click CLI test runner."""
        return CliRunner()
    
    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'AWS Lambda API Gateway Integration CLI' in result.output
    
    @patch.object(APIGatewayLambdaIntegration, 'create_api')
    @patch.object(APIGatewayLambdaIntegration, '_create_session')
    def test_create_api_command(self, mock_create_session, mock_create_api, runner):
        """Test create-api command."""
        # Mock session
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        
        # Mock create_api response
        api_result = {
            'api_id': 'api123',
            'api_name': 'test-api',
            'lambda_name': 'test-lambda',
            'lambda_arn': 'arn:aws:lambda:us-east-1:123456789012:function:test-lambda',
            'invoke_url': 'https://api123.execute-api.us-east-1.amazonaws.com/prod/test-lambda',
            'deployment_id': 'deployment123',
            'stage': 'prod'
        }
        mock_create_api.return_value = api_result
        
        # Call the command
        result = runner.invoke(cli, [
            'create-api',
            '--api-name', 'test-api',
            '--lambda-name', 'test-lambda',
            '--description', 'Test API',
            '--profile', 'test-profile',
            '--region', 'us-east-1'
        ])
        
        # Verify the result
        assert result.exit_code == 0
        assert 'API Gateway created successfully!' in result.output
        assert 'API ID: api123' in result.output
        assert 'API Name: test-api' in result.output
        assert 'Lambda Function: test-lambda' in result.output
        assert 'Invoke URL: https://api123.execute-api.us-east-1.amazonaws.com/prod/test-lambda' in result.output
        
        # Verify mock was called with correct arguments
        mock_create_api.assert_called_with('test-api', 'test-lambda', 'Test API')
    
    @patch.object(APIGatewayLambdaIntegration, 'create_api')
    def test_create_api_command_json_output(self, mock_create_api, runner):
        """Test create-api command with JSON output."""
        # Mock create_api response
        api_result = {
            'api_id': 'api123',
            'api_name': 'test-api',
            'lambda_name': 'test-lambda',
            'lambda_arn': 'arn:aws:lambda:us-east-1:123456789012:function:test-lambda',
            'invoke_url': 'https://api123.execute-api.us-east-1.amazonaws.com/prod/test-lambda',
            'deployment_id': 'deployment123',
            'stage': 'prod'
        }
        mock_create_api.return_value = api_result
        
        # Call the command
        result = runner.invoke(cli, [
            'create-api',
            '--api-name', 'test-api',
            '--lambda-name', 'test-lambda',
            '--output', 'json'
        ])
        
        # Verify the result
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output == api_result
    
    @patch.object(APIGatewayLambdaIntegration, 'create_api')
    def test_create_api_command_error(self, mock_create_api, runner):
        """Test create-api command with error."""
        # Mock create_api to raise an exception
        mock_create_api.side_effect = ValueError('Lambda function not found')
        
        # Call the command
        result = runner.invoke(cli, [
            'create-api',
            '--api-name', 'test-api',
            '--lambda-name', 'test-lambda'
        ])
        
        # Verify the result
        assert result.exit_code == 1
        assert 'Error: Lambda function not found' in result.output
    
    @patch.object(APIGatewayLambdaIntegration, 'delete_api')
    @patch.object(APIGatewayLambdaIntegration, '_create_session')
    def test_delete_api_command(self, mock_create_session, mock_delete_api, runner):
        """Test delete-api command."""
        # Mock session
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        
        # Mock delete_api response
        mock_delete_api.return_value = {'status': 'deleted', 'api_id': 'api123'}
        
        # Call the command
        result = runner.invoke(cli, [
            'delete-api',
            '--api-id', 'api123',
            '--profile', 'test-profile'
        ])
        
        # Verify the result
        assert result.exit_code == 0
        assert 'API Gateway api123 deleted successfully!' in result.output
        
        # Verify mock was called with correct arguments
        mock_delete_api.assert_called_with('api123')
    
    @patch.object(APIGatewayLambdaIntegration, 'list_apis')
    @patch.object(APIGatewayLambdaIntegration, '_create_session')
    def test_list_apis_command(self, mock_create_session, mock_list_apis, runner):
        """Test list-apis command."""
        # Mock session
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        
        # Mock list_apis response
        apis = [
            {'id': 'api123', 'name': 'test-api-1', 'createdDate': '2023-01-01T00:00:00Z'},
            {'id': 'api456', 'name': 'test-api-2', 'createdDate': '2023-01-02T00:00:00Z'}
        ]
        mock_list_apis.return_value = apis
        
        # Call the command
        result = runner.invoke(cli, [
            'list-apis',
            '--profile', 'test-profile'
        ])
        
        # Verify the result
        assert result.exit_code == 0
        assert 'API Gateways:' in result.output
        assert 'ID: api123' in result.output
        assert 'Name: test-api-1' in result.output
        assert 'ID: api456' in result.output
        assert 'Name: test-api-2' in result.output
    
    @patch.object(APIGatewayLambdaIntegration, 'list_apis')
    def test_list_apis_command_empty(self, mock_list_apis, runner):
        """Test list-apis command with no APIs."""
        # Mock list_apis response
        mock_list_apis.return_value = []
        
        # Call the command
        result = runner.invoke(cli, ['list-apis'])
        
        # Verify the result
        assert result.exit_code == 0
        assert 'No API Gateways found.' in result.output
    
    @patch.object(APIGatewayLambdaIntegration, 'get_api')
    def test_get_api_command(self, mock_get_api, runner):
        """Test get-api command."""
        # Mock get_api response
        api = {
            'id': 'api123',
            'name': 'test-api',
            'description': 'Test API',
            'createdDate': '2023-01-01T00:00:00Z',
            'apiKeySource': 'HEADER',
            'endpointConfiguration': {'types': ['REGIONAL']}
        }
        mock_get_api.return_value = api
        
        # Call the command
        result = runner.invoke(cli, [
            'get-api',
            '--api-id', 'api123'
        ])
        
        # Verify the result
        assert result.exit_code == 0
        assert 'API Gateway Details:' in result.output
        assert 'ID: api123' in result.output
        assert 'Name: test-api' in result.output
        assert 'Description: Test API' in result.output
        assert 'API Key Source: HEADER' in result.output
        assert "Endpoint Configuration: ['REGIONAL']" in result.output
        
        # Verify mock was called with correct arguments
        mock_get_api.assert_called_with('api123')
    
    @patch.object(APIGatewayLambdaIntegration, 'test_invoke_api')
    def test_test_invoke_command(self, mock_test_invoke, runner):
        """Test test-invoke command."""
        # Mock test_invoke_api response
        invoke_result = {
            'status': 200,
            'statusCode': '200',
            'body': '{"result": "success"}'
        }
        mock_test_invoke.return_value = invoke_result
        
        # Call the command
        result = runner.invoke(cli, [
            'test-invoke',
            '--api-id', 'api123',
            '--resource-path', '/test-lambda',
            '--http-method', 'POST',
            '--body', '{"key": "value"}'
        ])
        
        # Verify the result
        assert result.exit_code == 0
        assert 'Test Invoke Result:' in result.output
        assert 'Status: 200' in result.output
        assert 'Status Code: 200' in result.output
        assert 'Response Body: {"result": "success"}' in result.output
        
        # Verify mock was called with correct arguments
        mock_test_invoke.assert_called_with('api123', '/test-lambda', 'POST', '{"key": "value"}')
    
    @patch.object(ProfileManager, 'list_profiles')
    def test_list_profiles_command(self, mock_list_profiles, runner):
        """Test list-profiles command."""
        # Mock list_profiles response
        profiles = ['default', 'dev', 'prod']
        mock_list_profiles.return_value = profiles
        
        # Call the command
        result = runner.invoke(cli, ['list-profiles'])
        
        # Verify the result
        assert result.exit_code == 0
        assert 'AWS Profiles:' in result.output
        assert 'default' in result.output
        assert 'dev' in result.output
        assert 'prod' in result.output
    
    @patch.object(ProfileManager, 'get_profile_info')
    def test_get_profile_info_command(self, mock_get_profile_info, runner):
        """Test get-profile-info command."""
        # Mock get_profile_info response
        profile_info = {
            'profile': 'test-profile',
            'account_id': '123456789012',
            'user_id': 'AIDAEXAMPLE',
            'arn': 'arn:aws:iam::123456789012:user/test-user',
            'region': 'us-east-1'
        }
        mock_get_profile_info.return_value = profile_info
        
        # Call the command
        result = runner.invoke(cli, [
            'get-profile-info',
            '--profile', 'test-profile'
        ])
        
        # Verify the result
        assert result.exit_code == 0
        assert 'Profile Information:' in result.output
        assert 'Profile: test-profile' in result.output
        assert 'Account ID: 123456789012' in result.output
        assert 'User ID: AIDAEXAMPLE' in result.output
        assert 'ARN: arn:aws:iam::123456789012:user/test-user' in result.output
        assert 'Region: us-east-1' in result.output
        
        # Verify mock was called with correct arguments
        mock_get_profile_info.assert_called_with('test-profile')

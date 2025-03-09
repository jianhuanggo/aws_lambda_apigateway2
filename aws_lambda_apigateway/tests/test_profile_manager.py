"""
Unit tests for the AWS profile manager.
"""
import json
from unittest.mock import patch, MagicMock

import boto3
import pytest
from botocore.exceptions import ProfileNotFound

from aws_lambda_apigateway.core.profile_manager import ProfileManager

class TestProfileManager:
    """
    Test cases for the ProfileManager class.
    """
    
    def test_list_profiles(self):
        """Test listing AWS profiles."""
        # Mock boto3.Session
        mock_session = MagicMock()
        mock_session.available_profiles = ['default', 'dev', 'prod']
        
        with patch('boto3.Session', return_value=mock_session):
            # Call the method
            profiles = ProfileManager.list_profiles()
            
            # Verify the result
            assert profiles == ['default', 'dev', 'prod']
    
    def test_get_session_with_profile(self):
        """Test getting a session with a specific profile."""
        with patch('boto3.Session') as mock_session:
            # Call the method
            ProfileManager.get_session(profile_name='test-profile', region_name='us-east-1')
            
            # Verify boto3.Session was called with the correct arguments
            mock_session.assert_called_with(profile_name='test-profile', region_name='us-east-1')
    
    def test_get_session_with_latest_profile(self):
        """Test getting a session with 'latest' profile."""
        with patch('boto3.Session') as mock_session:
            # Call the method
            ProfileManager.get_session(profile_name='latest', region_name='us-east-1')
            
            # Verify boto3.Session was called with the correct arguments
            mock_session.assert_called_with(region_name='us-east-1')
    
    def test_get_session_with_default_profile(self):
        """Test getting a session with default profile."""
        with patch('boto3.Session') as mock_session:
            # Call the method
            ProfileManager.get_session(region_name='us-east-1')
            
            # Verify boto3.Session was called with the correct arguments
            mock_session.assert_called_with(region_name='us-east-1')
    
    def test_get_session_profile_not_found(self):
        """Test getting a session with non-existent profile."""
        with patch('boto3.Session', side_effect=ProfileNotFound(profile='non-existent')):
            # Call the method and verify it raises ProfileNotFound
            with pytest.raises(ProfileNotFound):
                ProfileManager.get_session(profile_name='non-existent')
    
    def test_get_profile_info(self):
        """Test getting profile information."""
        # Mock session and STS client
        mock_session = MagicMock()
        mock_sts = MagicMock()
        mock_session.client.return_value = mock_sts
        mock_session.region_name = 'us-east-1'
        
        # Mock get_caller_identity response
        identity = {
            'Account': '123456789012',
            'UserId': 'AIDAEXAMPLE',
            'Arn': 'arn:aws:iam::123456789012:user/test-user'
        }
        mock_sts.get_caller_identity.return_value = identity
        
        with patch('aws_lambda_apigateway.core.profile_manager.ProfileManager.get_session', return_value=mock_session):
            # Call the method
            info = ProfileManager.get_profile_info(profile_name='test-profile')
            
            # Verify the result
            assert info['profile'] == 'test-profile'
            assert info['account_id'] == '123456789012'
            assert info['user_id'] == 'AIDAEXAMPLE'
            assert info['arn'] == 'arn:aws:iam::123456789012:user/test-user'
            assert info['region'] == 'us-east-1'
            
            # Verify get_session was called with the correct arguments
            mock_session.client.assert_called_with('sts')
            mock_sts.get_caller_identity.assert_called_once()

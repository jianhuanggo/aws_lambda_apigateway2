"""
AWS profile management functionality.
"""
import logging
import os
from typing import Dict, List, Optional, Any

import boto3
from botocore.exceptions import ClientError, ProfileNotFound

logger = logging.getLogger(__name__)

class ProfileManager:
    """
    Class to manage AWS profiles.
    """
    
    @staticmethod
    def list_profiles() -> List[str]:
        """
        List all available AWS profiles.
        
        Returns:
            List of profile names.
        """
        try:
            session = boto3.Session()
            profiles = session.available_profiles
            logger.info(f"Found {len(profiles)} AWS profiles")
            return profiles
        except Exception as e:
            logger.error(f"Error listing AWS profiles: {e}")
            raise
    
    @staticmethod
    def get_session(profile_name: Optional[str] = None, region_name: Optional[str] = None) -> boto3.Session:
        """
        Get a boto3 session for the specified profile.
        
        Args:
            profile_name: AWS profile name to use. If 'latest', uses the latest credentials.
            region_name: AWS region name to use. If None, uses the default region.
            
        Returns:
            boto3.Session: The created session.
        """
        try:
            if profile_name == 'latest':
                # Use default session with latest credentials
                logger.info("Using latest AWS credentials")
                return boto3.Session(region_name=region_name)
            elif profile_name:
                logger.info(f"Using AWS profile: {profile_name}")
                return boto3.Session(profile_name=profile_name, region_name=region_name)
            else:
                logger.info("Using default AWS profile")
                return boto3.Session(region_name=region_name)
        except ProfileNotFound:
            logger.error(f"AWS profile not found: {profile_name}")
            raise
        except Exception as e:
            logger.error(f"Error creating AWS session: {e}")
            raise
    
    @staticmethod
    def get_profile_info(profile_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about an AWS profile.
        
        Args:
            profile_name: AWS profile name to get info for. If None, uses the default profile.
            
        Returns:
            Dict containing profile information.
        """
        try:
            session = ProfileManager.get_session(profile_name)
            sts_client = session.client('sts')
            identity = sts_client.get_caller_identity()
            
            return {
                'profile': profile_name or 'default',
                'account_id': identity['Account'],
                'user_id': identity['UserId'],
                'arn': identity['Arn'],
                'region': session.region_name
            }
        except Exception as e:
            logger.error(f"Error getting profile info: {e}")
            raise

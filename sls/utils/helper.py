"""
Module for AWS service and external validation helper methods
"""

# pylint: disable = no-name-in-module,import-error,no-self-use,broad-except,C0413,C0411

import os
import logging
import json
import boto3

# Logger setup
LOG_LEVEL = 'log_level'
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get(LOG_LEVEL, logging.ERROR))

def retrieve_secret(secret_key, region_name="us-east-1", boto_client=None):
    """
    Retrieve secret from secrets manager
    Args:
        secret_key: key to aws secret manager to retrieve
        region_name: aws account region name (default: us-east-1)
        boto_client: secrets manager boto3 client instance (optional)
    Returns:
        (str): plain text secret
    """
    # if not boto_client:
    #     boto_client = boto3.client('secretsmanager', region_name=region_name)
    LOGGER.info("SecretsManager: Retrieving secret for %s", secret_key)
    # secret_response = boto_client.get_secret_value(
    #     SecretId=str(secret_key),
    #     VersionStage='AWSCURRENT'
    # )
    # return secret_response['SecretString']
    return '{"password": "mock_password"}'

def parse_secret(secret):
    """
    Helper to parses secret from secrets manager/ssm parameter store
    Args:
        secret: json string of format {"PASSWORD": "service_account_password"}
    Returns:
        str: plaintext password
    """
    return json.loads(secret)['PASSWORD']

def verify_ami_image_id_exists(image_id, region_name, credentials, boto_client=None):
    """
    Helper to verfy if the given ami image id exists in aws account
    Args:
        image_id (str): ec2 ami image id (eg: ami-23wd24222d42)
        region_name (str): aws account region name (eg: us-east-1)
        credentials (dict): aws credentials dict object (AccessKeyId, SecretAccessKey, SessionToken)
        boto_client (object): ec2 boto3 client instance (optional)
    Returns:
        bool: True/False
    """
    if not boto_client:
        boto_client = boto3.client(
            service_name='ec2',
            region_name=region_name,
            aws_access_key_id=credentials.get('AccessKeyId', ''),
            aws_secret_access_key=credentials.get('SecretAccessKey', ''),
            aws_session_token=credentials.get('SessionToken', ''))
    result = boto_client.describe_images(ImageIds=[image_id])
    LOGGER.debug("ami: %s", result)
    if result and len(result.get('Images', []))==1 and result.get('Images')[0].get('ImageId'):
        return True
    return False

def verify_vpc_id_exists(vpc_id, region_name, credentials, boto_client=None):
    """
    Helper to verfy if the given vpc id exists in aws account
    Args:
        vpc_id (str): aws vpc id (eg: vpc-23wd24222d42)
        region_name (str): aws account region name (eg: us-east-1)
        credentials (dict): aws credentials dict object (AccessKeyId, SecretAccessKey, SessionToken)
        boto_client (object): ec2 boto3 client instance (optional)
    Returns:
        bool: True/False
    """
    if not boto_client:
        boto_client = boto3.client(
            service_name='ec2',
            region_name=region_name,
            aws_access_key_id=credentials.get('AccessKeyId', ''),
            aws_secret_access_key=credentials.get('SecretAccessKey', ''),
            aws_session_token=credentials.get('SessionToken', ''))
    result = boto_client.describe_vpcs(VpcIds=[vpc_id])
    if result and len(result.get('Vpcs', []))==1 and result.get('Vpcs')[0].get('VpcId'):
        return True
    return False

def get_ami_id(ssm_param_path, region='us-east-1'):
    """
    Helper to retrieve amazon's official public ami image id for given region
    Args:
        ssm_param_path (str): aws vpc id (eg: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2)
        region_name (str): aws account region name (default: us-east-1)
    Returns:
        str: ami image id
    """
    client = boto3.client('ssm', region_name=region)
    amzn_amis = client.get_parameter(Name=ssm_param_path)
    return amzn_amis['Parameter']['Value']

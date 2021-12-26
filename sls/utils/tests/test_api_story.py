# pylint: disable = no-name-in-module,missing-module-docstring,import-error,no-self-use,broad-except, C0413, C0411

import os
import sys
import logging
from unittest import TestCase
import unittest
from utils import api_core, data_objects, exceptions, helper, awsapi

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(BASE_PATH)

from utils.tests import config

LOG_LEVEL = 'log_level'
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get(LOG_LEVEL, logging.ERROR))

class TestStory(TestCase):
    """[story]"""
    def test_ami_mgmt_contoller_put_bad_account(self):
        """Failure in adding AMI when VPCx account is invalid"""
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception",
            "path": "/v1/accounts/non-acc/regions/us-east-1/amis/ami-00dfe2c7ce89a450b/vpcs/*/ami_exception",
            "httpMethod": "PUT",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "image_id": "ami-00dfe2c7ce89a450b",
                "region_name": "us-east-1",
                "account_id": "non-acc",
                "vpc_id": "*"
            }
        }
        with self.assertRaises(exceptions.AccountNotFound):
            api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))

    def test_ami_mgmt_contoller_put_bad_region(self):
        """Failure in adding AMI when region is invalid"""
        account = config['behave']['account']
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception",
            "path": f"/v1/accounts/{account}/regions/no-region-1/amis/ami-00dfe2c7ce89a450b/vpcs/*/ami_exception",
            "httpMethod": "PUT",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "image_id": "ami-00dfe2c7ce89a450b",
                "region_name": "no-region-1",
                "account_id": account,
                "vpc_id": "*"
            }
        }
        with self.assertRaises(exceptions.InvalidInputException):
            api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))

    def test_ami_mgmt_contoller_put_wildcard_region(self):
        """Failure in adding AMI when region is wildcard"""
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception",
            "path": "/v1/accounts/itx-016/regions/*/amis/ami-00dfe2c7ce89a450b/vpcs/*/ami_exception",
            "httpMethod": "PUT",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "image_id": "ami-00dfe2c7ce89a450b",
                "region_name": "*",
                "account_id": "itx-016",
                "vpc_id": "*"
            }
        }
        with self.assertRaises(Exception):
            api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))

    def test_ami_mgmt_contoller_put_wildcard_account(self):
        """Failure in adding Exempt AMI when AMI, VPC and region are provided, but account is wildcard"""
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception",
            "path": "/v1/accounts/*/regions/us-east-1/amis/ami-00dfe2c7ce89a450b/vpcs/*/ami_exception",
            "httpMethod": "PUT",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "image_id": "ami-00dfe2c7ce89a450b",
                "region_name": "us-east-1",
                "account_id": "*",
                "vpc_id": "*"
            }
        }
        with self.assertRaises(Exception):
            api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))

    def test_process_ami_exception_list_commmon_second_vpc(self):
        """Success in adding a new AMI exception with a second VPC for a region while an exception already exists for first VPC"""
        payload_current_exceptions = [
            "ami-6343|us-east-1|vpc-4564"
        ]
        expected_exceptions = [
            "ami-6343|us-east-1|vpc-2341",
            "ami-6343|us-east-1|vpc-4564"
        ]
        payload_new_image = {
            "image_id": "ami-6343",
            "region_name": "us-east-1",
            "account_id": "itx-000",
            "vpc_id": "vpc-2341"
        }
        result = api_core.process_ami_exception_list(
            data_objects.unmarshall_exception_image_vars(payload_new_image),
            payload_current_exceptions
        )
        self.assertEqual(sorted(result), sorted(expected_exceptions))

    def test_ami_mgmt_contoller_bad_vpc(self):
        """Failure in adding AMI when VPC is not wildcard and is invalid"""
        region = config['main']['region']
        account = config['behave']['account']
        ami_id = helper.get_ami_id('/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2', region)
        vpc_id = "bad_vpc_id"
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception",
            "path": f"/v1/accounts/{account}/regions/{region}/amis/{ami_id}/vpcs/{vpc_id}/ami_exception",
            "httpMethod": "PUT",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "image_id": ami_id,
                "region_name": region,
                "account_id": account,
                "vpc_id": vpc_id
            }
        }
        with self.assertRaises(Exception):
            api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))

    def test_ami_mgmt_contoller_bad_ami(self):
        """Failure in adding AMI when AMI is not wildcard and is not found"""
        region = config['main']['region']
        account = config['behave']['account']
        ami_id = "bad-ami-id"
        vpc_id = config['behave']['vpc_id']
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception",
            "path": f"/v1/accounts/{account}/regions/{region}/amis/{ami_id}/vpcs/{vpc_id}/ami_exception",
            "httpMethod": "PUT",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "image_id": ami_id,
                "region_name": region,
                "account_id": account,
                "vpc_id": vpc_id
            }
        }
        with self.assertRaises(Exception):
            api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))

    def test_ami_mgmt_contoller_bad_ami_vpc(self):
        """Failure in adding Exempt AMI when AMI and VPC is wildcard"""
        region = config['main']['region']
        account = config['behave']['account']
        ami_id = "bad-ami-id"
        vpc_id = "bad_vpc_id"
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception",
            "path": f"/v1/accounts/{account}/regions/{region}/amis/{ami_id}/vpcs/{vpc_id}/ami_exception",
            "httpMethod": "PUT",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "image_id": ami_id,
                "region_name": region,
                "account_id": account,
                "vpc_id": vpc_id
            }
        }
        with self.assertRaises(Exception):
            api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))

    def test_verify_request_authorization(self):
        """Failure in adding AMI when API user is not authorized"""
        headers = {
            'Authorization': '<token>',
            "Content-Type": "application/json",
        }
        ldap_config = data_objects.unmarshall_ldap_env_vars(os.environ)
        logger.debug(ldap_config)
        with self.assertRaises(Exception):
            awsapi.verify_request_authorization({'headers': headers}, ldap_config)

if __name__ == '__main__':
    unittest.main()

# pylint: disable = no-name-in-module,missing-module-docstring,import-error,no-self-use,broad-except, C0413, C0411

import os
import sys
from unittest import TestCase
import unittest
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(BASE_PATH)
module_dir = os.path.dirname(os.path.abspath(__file__))
module_par = os.path.normpath(os.path.join(module_dir, '../../../'))
sys.path.append(module_par)
from utils import api_core, data_objects, exceptions, helper
from utils.tests import config

class TestAPICore(TestCase):
    """[api-core]"""

    def test_process_ami_exception_list_vpc_1(self):
        """Success in vpc upgrade"""
        payload_current_exceptions = [
            "ami-1232|us-east-1|vpc-2341",
            "ami-1232|us-east-1|vpc-35r4",
            "ami-6343|us-east-1|vpc-2341",
            "ami-3453|us-east-1|*",
            "*|us-east-1|vpc-5476"
        ]
        expected_exceptions = [
            "ami-1232|us-east-1|*",
            "ami-6343|us-east-1|vpc-2341",
            "ami-3453|us-east-1|*",
            "*|us-east-1|vpc-5476"
        ]
        payload_new_image = {
            "image_id": "ami-1232",
            "region_name": "us-east-1",
            "account_id": "itx-000",
            "vpc_id": "*"
        }
        result = api_core.process_ami_exception_list(
            data_objects.unmarshall_exception_image_vars(payload_new_image),
            payload_current_exceptions
        )
        self.assertEqual(sorted(result), sorted(expected_exceptions))

    def test_process_ami_exception_list_vpc_2(self):
        """Success in vpc upgrade when ami is *"""
        payload_current_exceptions = [
            "*|us-east-1|vpc-2341",
            "ami-6343|us-east-1|vpc-4564",
            "ami-3453|us-east-1|*"
        ]
        expected_exceptions = [
            "ami-1232|us-east-1|*",
            "*|us-east-1|vpc-2341",
            "ami-6343|us-east-1|vpc-4564",
            "ami-3453|us-east-1|*"
        ]
        payload_new_image = {
            "image_id": "ami-1232",
            "region_name": "us-east-1",
            "account_id": "itx-000",
            "vpc_id": "*"
        }
        result = api_core.process_ami_exception_list(
            data_objects.unmarshall_exception_image_vars(payload_new_image),
            payload_current_exceptions
        )
        self.assertEqual(sorted(result), sorted(expected_exceptions))

    def test_process_ami_exception_list_ami_1(self):
        """Success in ami upgrade"""
        payload_current_exceptions = [
            "ami-1232|us-east-1|vpc-2341",
            "ami-1232|us-east-1|vpc-35r4",
            "ami-6343|us-east-1|vpc-2341",
            "ami-3453|us-east-1|*",
            "*|us-east-1|vpc-5476"
        ]
        expected_exceptions = [
            "ami-1232|us-east-1|vpc-35r4",
            "*|us-east-1|vpc-2341",
            "ami-3453|us-east-1|*",
            "*|us-east-1|vpc-5476"
        ]
        payload_new_image = {
            "image_id": "*",
            "region_name": "us-east-1",
            "account_id": "itx-000",
            "vpc_id": "vpc-2341"
        }
        result = api_core.process_ami_exception_list(
            data_objects.unmarshall_exception_image_vars(payload_new_image),
            payload_current_exceptions
        )
        self.assertEqual(sorted(result), sorted(expected_exceptions))

    def test_process_ami_exception_list_ami_2(self):
        """Success in ami upgrade when vpc is *"""
        payload_current_exceptions = [
            "*|us-east-1|vpc-2341",
            "ami-6343|us-east-1|vpc-4564",
            "ami-3453|us-east-1|*"
        ]
        expected_exceptions = [
            "*|us-east-1|vpc-35r4",
            "*|us-east-1|vpc-2341",
            "ami-6343|us-east-1|vpc-4564",
            "ami-3453|us-east-1|*"
        ]
        payload_new_image = {
            "image_id": "*",
            "region_name": "us-east-1",
            "account_id": "itx-000",
            "vpc_id": "vpc-35r4"
        }
        result = api_core.process_ami_exception_list(
            data_objects.unmarshall_exception_image_vars(payload_new_image),
            payload_current_exceptions
        )
        self.assertEqual(sorted(result), sorted(expected_exceptions))

    def test_process_ami_exception_list_common_1(self):
        """Success in vpc downgrade when ami is upgraded"""
        payload_current_exceptions = [
            "ami-1232|us-east-1|*",
            "*|us-east-1|vpc-2341",
            "ami-6343|us-east-1|vpc-4564",
            "ami-3453|us-east-1|*"
        ]
        expected_exceptions = [
            "ami-1232|us-east-1|vpc-2341",
            "ami-6343|us-east-1|vpc-4564",
            "ami-3453|us-east-1|*"
        ]
        payload_new_image = {
            "image_id": "ami-1232",
            "region_name": "us-east-1",
            "account_id": "itx-000",
            "vpc_id": "vpc-2341"
        }
        result = api_core.process_ami_exception_list(
            data_objects.unmarshall_exception_image_vars(payload_new_image),
            payload_current_exceptions
        )
        self.assertEqual(sorted(result), sorted(expected_exceptions))

    def test_process_ami_exception_list_commmon_2(self):
        """Success in ami exception ami add"""
        payload_current_exceptions = [
            "ami-1232|us-east-1|*",
            "ami-6343|us-east-1|vpc-4564",
            "ami-3453|us-east-1|*"
        ]
        expected_exceptions = [
            "ami-1232|us-east-1|*",
            "ami-9872|us-east-1|vpc-2341",
            "ami-6343|us-east-1|vpc-4564",
            "ami-3453|us-east-1|*"
        ]
        payload_new_image = {
            "image_id": "ami-9872",
            "region_name": "us-east-1",
            "account_id": "itx-000",
            "vpc_id": "vpc-2341"
        }
        result = api_core.process_ami_exception_list(
            data_objects.unmarshall_exception_image_vars(payload_new_image),
            payload_current_exceptions
        )
        self.assertEqual(sorted(result), sorted(expected_exceptions))

    def test_ami_mgmt_contoller_put_unknown(self):
        """Failure in request for unknown resource"""
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/ec2_exception",
            "path": f"/v1/accounts/{config['behave']['account']}/regions/us-east-1/ec2_exception",
            "httpMethod": "PUT",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "region_name": "us-east-1",
                "account_id": config['behave']['account']
            }
        }
        with self.assertRaises(exceptions.ResourceUnknownException):
            api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))

    def test_ami_mgmt_contoller_put_ok(self):
        """Success in put request for ami exception"""
        region = config['main']['region']
        account = config['behave']['account']
        ami_id = helper.get_ami_id('/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2', region)
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception",
            "path": f"/v1/accounts/{account}/regions/{region}/amis/{ami_id}/vpcs/*/ami_exception",
            "httpMethod": "PUT",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "image_id": ami_id,
                "region_name": region,
                "account_id": account,
                "vpc_id": "*"
            }
        }
        result = api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))
        self.assertEqual(result.statusCode, 200)

    def test_ami_mgmt_contoller_delete_ok(self):
        """Success in delete request for ami exception"""
        region = config['main']['region']
        account = config['behave']['account']
        ami_id = helper.get_ami_id('/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2', region)
        payload_event = {
            "resource": "/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception",
            "path": f"/v1/accounts/{account}/regions/{region}/amis/{ami_id}/vpcs/*/ami_exception",
            "httpMethod": "DELETE",
            "headers": {"Authorization": "<token>"},
            "pathParameters": {
                "image_id": ami_id,
                "region_name": region,
                "account_id": account,
                "vpc_id": "*"
            }
        }
        result = api_core.ami_mgmt_contoller(data_objects.unmarshall_api_gateway_event(payload_event))
        self.assertEqual(result.statusCode, 200)

if __name__ == '__main__':
    unittest.main()

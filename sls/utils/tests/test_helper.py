"""
Test aws and validation helpers
"""

# pylint: disable = no-name-in-module,import-error,no-self-use,broad-except, C0413, C0411

import os, sys
import boto3
from unittest import TestCase
import unittest
from moto import mock_secretsmanager, mock_ec2
module_dir = os.path.dirname(os.path.abspath(__file__))
module_par = os.path.normpath(os.path.join(module_dir, '../../../'))
sys.path.append(module_par)
from sls.utils import helper
# from sls.utils import data_objects

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

class TestHelper(TestCase):
    """[helper]"""

    def test_parse_secret(self):
        """Success in parsing password secret json"""
        result = helper.parse_secret('{"PASSWORD": "mock_password"}')
        self.assertEqual(result, 'mock_password')

    @mock_secretsmanager
    def test_retrieve_secret(self):
        """Success in get passord from secret manger"""
        conn = boto3.client("secretsmanager", region_name="us-east-1")
        conn.create_secret(
            Name="xbot2-test-password", SecretString="mock_password"
        )
        result = helper.retrieve_secret("xbot2-test-password", "us-east-1", conn)
        self.assertEqual(result, 'mock_password')

    @mock_ec2
    def test_verify_ami_image_id_exists_true(self):
        """Success in if AMI exists"""
        conn = boto3.client("ec2", region_name="us-east-1")
        # this test AMI ID is from moto/ec2/resources/amis.json
        test_ami_id = "ami-03cf127a"
        result = helper.verify_ami_image_id_exists(test_ami_id, "us-east-1", None, conn)
        self.assertTrue(result)

    @mock_ec2
    def test_verify_ami_image_id_exists_false(self):
        """Failure in if AMI exists"""
        conn = boto3.client("ec2", region_name="us-east-1")
        with self.assertRaises(Exception):
            helper.verify_ami_image_id_exists("ami-no-exists", "us-east-1", None, conn)

    @mock_ec2
    def test_verify_vpc_id_exists_true(self):
        """Success in if VPC exists"""
        conn = boto3.client("ec2", region_name="us-east-1")
        vpc_response = conn.create_vpc(CidrBlock='10.0.0.0/24')
        result = helper.verify_vpc_id_exists(vpc_response['Vpc']['VpcId'], "us-east-1", None, conn)
        self.assertTrue(result)

    @mock_ec2
    def test_verify_vpc_id_exists_false(self):
        """Failure in if VPC exists"""
        conn = boto3.client("ec2", region_name="us-east-1")
        with self.assertRaises(Exception):
            helper.verify_vpc_id_exists("vpc-no-exists", "us-east-1", None, conn)

if __name__ == '__main__':
    unittest.main()
    
# pylint: disable = no-name-in-module,missing-module-docstring,import-error,no-self-use,broad-except, C0413, C0411

import os
import sys
from unittest import TestCase
from unittest.mock import patch
import unittest
from utils import awsapi, data_objects

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(BASE_PATH)

from utils.tests import config

class TestAWSApi(TestCase):
    """[awsapi]"""

    #@patch("utils.helper.retrieve_secret", return_value="mock_pwd")
    # def test_get_aws_credentials_for_account(self):
    #     """Success in retrieving credential"""
    #     account = config['behave']['account']
    #     vpciam_config = data_objects.unmarshall_vpcx_iam_vars(os.environ)
    #     # with self.assertRaises(Exception):
    #     #     helper.get_aws_credentials_for_account(account', vpciam_config)
    #     result = awsapi.get_aws_credentials_for_account(account, vpciam_config)
    #     self.assertAlmostEqual(len(result), 4)

if __name__ == '__main__':
    unittest.main()

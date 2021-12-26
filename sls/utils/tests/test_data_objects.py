# pylint: disable = bad-option-value,no-name-in-module,missing-module-docstring,import-error,no-self-use,broad-except, C0413, C0411, C0330

import os, sys
from unittest import TestCase
import unittest

module_dir = os.path.dirname(os.path.abspath(__file__))
module_par = os.path.normpath(os.path.join(module_dir, '../../../'))
sys.path.append(module_par)
from utils.data_objects import unmarshall_exception_image_vars
from utils.data_objects import unmarshall_api_gateway_event
from utils.data_objects import Ldap, unmarshall_ldap_env_vars
from utils.data_objects import VpcxIam, unmarshall_vpcx_iam_vars
from utils.data_objects import Response

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

class TestDataObjects(TestCase):
    """[Data Obj]"""
    def test_unmarshall_exception_image_vars(self):
        """Success in unmarshall exception image params"""
        payload = {
            "image_id": "ami-0652346abb029e48a",
            "region_name": "us-east-1",
            "account_id": "itx-000",
            "vpc_id": "*"
        }
        result = unmarshall_exception_image_vars(payload)
        self.assertEqual(result.image_id, 'ami-0652346abb029e48a')
        self.assertEqual(result.region_name, 'us-east-1')
        self.assertEqual(result.account_id, 'itx-000')
        self.assertEqual(result.vpc_id, "*")

    def test_unmarshall_api_gateway_event(self):
        """Success in unmarshall api gateway event"""
        payload_event = {
            "resource": "/v1/goldenimage/",
            "path": "/v1/goldenimage/",
            "httpMethod": "PUT",
            "pathParameters": {"image_id": "ami-0652346abb029e48a", "region_name": "us-east-1"}
        }

        expected_result_object = {
            'path': '/v1/goldenimage/',
            'resource': '/v1/goldenimage/',
            'http_method': 'PUT',
            'headers': None,
            'query_string_parameters': None,
            'path_parameters': {'image_id': 'ami-0652346abb029e48a', 'region_name': 'us-east-1'},
            'stage_variables': None,
            'request_context': None,
            'body': None,
            'multi_value_headers': None,
            'multi_value_query_string_parameters': None
        }

        result = unmarshall_api_gateway_event(payload_event)
        self.assertEqual(expected_result_object, result.__dict__)

    def test_response(self):
        """Success in Response object creation"""
        expected_result_object = {
            "statusCode": 200,
            "isBase64Encoded": False,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            "body": "{\"success_add\": \"AMI added [ami-0652346abb029e48a, us-east-1, *, *].\"}"
        }

        result = Response(200, body='{"success_add": "AMI added [ami-0652346abb029e48a, us-east-1, *, *]."}')
        self.assertEqual(expected_result_object, result.__dict__)

    def test_ldap(self):
        """Success in LDAP config object creation"""
        expected_result_object = {
            'ldap_server': 'ldap://nadir.test-org.com:3268',
            'ldap_username': 'savchook',
            'ldap_password_secret_name': 'ldap-password',
            'ldap_search_base': 'dc=test-org,dc=com',
            'ldap_object_class': 'person',
            'ldap_group_name': ['its-ep-app-itxvpcx-itxadmins'],
            'ldap_lookup_attribute': 'userprincipalname',
            'msft_idp_tenant_id': '3ac94b33-9135-4821-9502-eafda6592a35',
            'msft_idp_app_id': ['https://clx-awsapi-ami-management-dev.test-org.com'],
            'msft_idp_client_roles': ['writer']
        }

        result = Ldap(
                    ldap_server='ldap://nadir.test-org.com:3268',
                    ldap_username='savchook',
                    ldap_password_secret_name='ldap-password',
                    ldap_search_base='dc=test-org,dc=com',
                    ldap_object_class='person',
                    ldap_group_name=['its-ep-app-itxvpcx-itxadmins'],
                    ldap_lookup_attribute='userprincipalname',
                    msft_idp_tenant_id='3ac94b33-9135-4821-9502-eafda6592a35',
                    msft_idp_app_id=['https://clx-awsapi-ami-management-dev.test-org.com'],
                    msft_idp_client_roles=['writer'])
        # self.assertEqual(result.ldap_server, 'ldap://nadir.test-org.com:3268')
        self.assertEqual(expected_result_object, result.__dict__)

    def test_unmarshall_ldap_env_vars(self):
        """Success in unmarshall LDAP config env vars"""
        payload = {
            'ldap_server': 'ldap://nadir.test-org.com:3268',
            'ldap_username': 'savchook',
            'ldap_password_secret_name': 'ldap-password',
            'ldap_search_base': 'dc=test-org,dc=com',
            'ldap_object_class': 'person',
            'ldap_group_name': 'its-ep-app-itxvpcx-itxadmins',
            'ldap_lookup_attribute': 'userprincipalname',
            'msft_idp_tenant_id': '3ac94b33-9135-4821-9502-eafda6592a35',
            'msft_idp_app_id': 'https://clx-awsapi-ami-management-dev.test-org.com',
            'msft_idp_client_roles': 'writer'
        }
        expected_result_object = {
            'ldap_server': 'ldap://nadir.test-org.com:3268',
            'ldap_username': 'savchook',
            'ldap_password_secret_name': 'ldap-password',
            'ldap_search_base': 'dc=test-org,dc=com',
            'ldap_object_class': 'person',
            'ldap_group_name': ['its-ep-app-itxvpcx-itxadmins'],
            'ldap_lookup_attribute': 'userprincipalname',
            'msft_idp_tenant_id': '3ac94b33-9135-4821-9502-eafda6592a35',
            'msft_idp_app_id': ['https://clx-awsapi-ami-management-dev.test-org.com'],
            'msft_idp_client_roles': ['writer']
        }
        result = unmarshall_ldap_env_vars(payload)
        self.assertEqual(expected_result_object, result.__dict__)

    def test_vpcxaim(self):
        """Success in vpcxiam config object creation"""
        expected_result_object = {
            'endpoint': 'https://vpce-012710b591427fc69-kykwwlo6.execute-api.us-east-1.vpce.amazonaws.com/dev',
            'host': 'pygqxstmyi.execute-api.us-east-1.amazonaws.com',
            'scope': 'https://clx-awsapi-credential-dev.test-org.com/.default',
            'token_url': 'https://login.microsoftonline.com/test-org.onmicrosoft.com/oauth2/v2.0/token',
            'client_id': "https://clx-awsapi-tagging-dev.test-org.com",
            'secret_name': "nextbot/resource_tagging"
        }
        result = VpcxIam(
            endpoint='https://vpce-012710b591427fc69-kykwwlo6.execute-api.us-east-1.vpce.amazonaws.com/dev',
            host='pygqxstmyi.execute-api.us-east-1.amazonaws.com',
            scope='https://clx-awsapi-credential-dev.test-org.com/.default',
            token_url='https://login.microsoftonline.com/test-org.onmicrosoft.com/oauth2/v2.0/token',
            client_id="https://clx-awsapi-tagging-dev.test-org.com",
            secret_name="nextbot/resource_tagging")
        self.assertEqual(sorted(expected_result_object), sorted(result.__dict__))

    def test_unmarshall_vpcx_iam_vars(self):
        """Success in unmarshall vpcx iam vars"""
        payload = {
            'vpcxiam_endpoint': 'https://vpce-012710b591427fc69-kykwwlo6.execute-api.us-east-1.vpce.amazonaws.com/dev',
            'vpcxiam_host': 'pygqxstmyi.execute-api.us-east-1.amazonaws.com',
            'vpcxiam_scope': 'https://clx-awsapi-credential-dev.test-org.com/.default',
            'vpcxiam_token_url': 'https://login.microsoftonline.com/test-org.onmicrosoft.com/oauth2/v2.0/token',
            'vpcxiam_client_id': "https://clx-awsapi-tagging-dev.test-org.com",
            'vpcxiam_secret_name': "nextbot/resource_tagging"
        }
        expected_result_object = {
            'endpoint': 'https://vpce-012710b591427fc69-kykwwlo6.execute-api.us-east-1.vpce.amazonaws.com/dev',
            'host': 'pygqxstmyi.execute-api.us-east-1.amazonaws.com',
            'scope': 'https://clx-awsapi-credential-dev.test-org.com/.default',
            'token_url': 'https://login.microsoftonline.com/test-org.onmicrosoft.com/oauth2/v2.0/token',
            'client_id': "https://clx-awsapi-tagging-dev.test-org.com",
            'secret_name': "nextbot/resource_tagging"
        }
        result = unmarshall_vpcx_iam_vars(payload)
        self.assertEqual(sorted(expected_result_object), sorted(result.__dict__))

if __name__ == '__main__':
    unittest.main()

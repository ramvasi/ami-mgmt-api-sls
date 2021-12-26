"""
Data Object module
"""

# pylint: disable = no-name-in-module,import-error,no-self-use,broad-except, C0413, C0411

from typing import List
from dataclasses import dataclass, field
from sls.utils.exceptions import InvalidInputException

@dataclass(frozen=True)
class ImageData:
    """dao for capturing ami image id and meta data"""
    image_id: str
    region_name: str
    account_id: str
    vpc_id: str

def unmarshall_exception_image_vars(path_params: dict):
    """
    Unmarshalls exception ami image realted metadata from path param
    Args:
        path_params (dict): url path parameters as a dict object
    Return:
        ImageData: ami image dao
    """
    region_name = path_params.get('region_name', '').strip().lower()
    image_id = path_params.get('image_id', '').strip().lower()
    account_id = path_params.get('account_id', '').strip().lower()
    vpc_id = path_params.get('vpc_id', '').strip().lower()

    if not account_id:
        raise InvalidInputException("Please provide a valid account in the url path")

    if "*" in account_id:
        raise InvalidInputException("Account name cannot be or contain a wild character")

    if not region_name:
        raise InvalidInputException("Please provide a valid region name in the url path")

    if "*" in region_name:
        raise InvalidInputException("Region cannot be or contain a wild character")

    if not image_id:
        raise InvalidInputException("Please provide a valid AMI image id in the url path")

    if not vpc_id:
        raise InvalidInputException("Please provide a valid VPC id in the url path")

    if image_id=="*" and vpc_id=="*":
        raise InvalidInputException("Both VPC id and AMI image id cannot be wildcard")

    return ImageData(
        region_name=region_name,
        image_id=image_id,
        account_id=account_id,
        vpc_id=vpc_id)

@dataclass(frozen=True)
class Request:
    """dao for api request object"""
    path: str
    resource: str
    http_method: str
    headers: dict
    query_string_parameters: dict
    path_parameters: dict
    stage_variables: dict
    request_context: dict
    body: str
    multi_value_headers: dict = field(default_factory=lambda: {})
    multi_value_query_string_parameters: dict = field(default_factory=lambda: {})

def unmarshall_api_gateway_event(event: dict):
    """
    Unmarshalls request object from API Gateway event
    Args:
        event (dict): API Gateway event
    Returns:
        Request: request dao
    """
    return Request(path=event['path'],
                   http_method=event['httpMethod'],
                   resource=event['resource'],
                   headers=event.get('headers', None),
                   multi_value_headers=event.get('multiValueHeaders', None),
                   query_string_parameters=event.get('queryStringParameters', None),
                   multi_value_query_string_parameters=event.get(
                       'multiValueQueryStringParameters', None),
                   path_parameters=event.get('pathParameters', None),
                   stage_variables=event.get('stageVariables', None),
                   request_context=event.get('requestContext', None),
                   body=event.get('body', None))

@dataclass
class Response:
    """dao for api response object"""
    # pylint: disable=invalid-name
    statusCode: int
    isBase64Encoded: bool = False
    headers: dict = field(
        default_factory=lambda: {
            "Content-Type": 'application/json',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True
        })
    body: str = ""

    def set_header(self, key: str, value: str):
        """
        set additonal response header
        Args:
            key (str): header key to add
            value (str): header value to add
        Returns:
            None
        """
        self.headers[key] = value

# Define LDAP lookup configs
@dataclass(frozen=True)
class Ldap:
    """dao for ldap config helper object"""
    ldap_server: str
    ldap_username: str
    ldap_password_secret_name: str
    ldap_search_base: str
    ldap_object_class: str
    ldap_group_name: List[str]
    ldap_lookup_attribute: str
    msft_idp_tenant_id: str
    msft_idp_app_id: List[str]
    msft_idp_client_roles: List[str]

def unmarshall_ldap_env_vars(env: dict):
    """
    Unmarshalls ldap config from OS environment
    Args:
        env (dict): dict object of environment variables
    Returns:
        Ldap: ldap dao
    """
    return Ldap(
        ldap_server=env['ldap_server'],
        ldap_username=env['ldap_username'],
        ldap_password_secret_name=env['ldap_password_secret_name'],
        ldap_search_base=env['ldap_search_base'],
        ldap_object_class=env['ldap_object_class'],
        ldap_group_name=env['ldap_group_name'].split(','),
        ldap_lookup_attribute=env['ldap_lookup_attribute'],
        msft_idp_tenant_id=env['msft_idp_tenant_id'],
        msft_idp_app_id=env['msft_idp_app_id'].split(','),
        msft_idp_client_roles=env['msft_idp_client_roles'].split(',')
    )

# VPCx IAM credential service config
@dataclass(frozen=True)
class VpcxIam:
    """dao for VPCx IAM credential service config object"""
    scope: str
    endpoint: str
    host: str
    token_url: str
    client_id: str
    secret_name: str

def unmarshall_vpcx_iam_vars(env: dict):
    """
    Unmarshalls app specific vars from OS environment
    Args:
        env (dict): dict object of environment variables
    Returns:
        VpcxIam: VpcxIam dao
    """
    return VpcxIam(
        scope=env.get('vpcxiam_scope'),
        endpoint=env.get('vpcxiam_endpoint'),
        host=env.get('vpcxiam_host'),
        token_url=env.get('vpcxiam_token_url'),
        client_id=env.get('vpcxiam_client_id'),
        secret_name=env.get('vpcxiam_secret_name')
    )

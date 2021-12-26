"""This module is used to validate and make API calls to AWSAPI Microservices"""

# pylint:disable= no-member, invalid-name, E0401, W1203, C0411

import os
import logging
#from azureauth.create_token import TokenGenerator
from requests import request
from utils import helper
from utils.exceptions import AuthorizationException
#from cloudx_sls_authorization import lambda_auth

HTTP_GET = 'get'
HTTP_PUT = 'put'
HTTP_POST = 'post'

# Logger setup
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get('log_level', logging.WARNING))

def verify_request_authorization(event, ldap_config):
    """
    Verifies if the lambda request is authorized
    Args:
        event (dict): lambda event object with authorization headers
        ldap_config (Ldap): ldap configuration parameter data object
    Returns:
        bool: True if authorization is successfull
    Raises:
        AuthorizationException: Authorization error
    """
    try:
        # lambda_auth.authorize_lambda_request(
        #     event,
        #     ldap_config.msft_idp_tenant_id,
        #     ldap_config.msft_idp_app_id,
        #     ldap_config.msft_idp_client_roles,
        #     ldap_config.ldap_server,
        #     ldap_config.ldap_username,
        #     helper.parse_secret(helper.retrieve_secret(
        #         ldap_config.ldap_password_secret_name)),
        #     ldap_config.ldap_search_base,
        #     ldap_config.ldap_object_class,
        #     ldap_config.ldap_group_name,
        #     ldap_config.ldap_lookup_attribute)
        pass
    except Exception as e:
        # traceback.print_exc()
        LOGGER.exception('Authorization error')
        raise AuthorizationException(str(e)) from e

    return True

def get_aws_credentials_for_account(account_id, vpciam_config):
    """
    Gets aws access key/secret for a given account for given application scope using cloudx credential service
    Args:
        account_id (str): vpcs project/account id
        vpciam_config (VpcxIam): cloudx credential service config parameter data object
    Returns:
        dict: aws credential object (key, secret, session, expiration)
    Raises:
        ValueError: error retrieving credentials
    """
    url = f"{vpciam_config.endpoint}/v1/accounts/{account_id}/roles/admin/credentials"
    additional_headers = {
        'Host': vpciam_config.host
    }
    access_token = get_access_token(
        vpciam_config.token_url,
        vpciam_config.client_id,
        helper.retrieve_secret(vpciam_config.secret_name),
        vpciam_config.scope
    )
    credentials = _send_request(
        url=url,
        method=HTTP_GET,
        access_token=access_token,
        additional_headers=additional_headers)
    error = credentials.get('error', {})
    if error:
        LOGGER.error(error)
        raise ValueError(error)
    return credentials.get('credentials', {})

def get_access_token(token_url: str, client_id: str, client_secret: str, scope: str):
    """
    Get an Access Token for the <scope> of the client
    Args:
        token_url (str): url endpoint for azure token server
        client_id (str): client id to get token.
        client_secret (str): client secret to get token.
        scope (str): Azure AD App registration scope | DEFAULT = VPCxIAM Default Scope.
    Returns:
        str: Azure AD Bearer Token
    """
    try:
        LOGGER.info("Generating Bearer token for scope '%s'.", scope)
        # generator = TokenGenerator(client_id, client_secret, token_url)
        # token = generator.get_bearer_token(scope)
        token = ""
    except Exception as ex:
        LOGGER.exception(ex)
        LOGGER.error("Failed to generated token for scope '%s' at url '%s'.", scope, token_url)
        raise ex
    return token

def _send_request(url: str, method: str, access_token: str,
                    additional_headers: dict = None,
                    additional_payload: dict = None):
    """
    Make a Http request to rest api url
    Args:
        url (str): API URL.
        method (str): Http method. Values = get / put / post
        access_token (str): authorization access token.
        additional_headers (dict): Additional request headers.
        additional_payload (dict): Additional request paylaod.
    Returns:
        dict: Response object of Http Request
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": access_token
        }
        if additional_headers:
            headers.update(additional_headers)
        kwargs = {
            "verify": False,
            "headers": headers
        }
        payload = {}
        if additional_payload:
            payload.update(additional_payload)
        if method in [HTTP_PUT, HTTP_POST]:
            kwargs["json"] = payload
        elif method in [HTTP_GET]:
            kwargs["params"] = payload
        else:
            raise Exception(f"Http Method type {method} not Supported")
        LOGGER.debug("[%s]%s (payload: %s)", method.upper(), url, payload)
        response = request(method, url, timeout=300, **kwargs)
        LOGGER.debug("get cred reponse: %s", response.status_code)
        return response.json()
    except Exception as ex:
        LOGGER.exception(ex)
        LOGGER.error("Failed to retreive credentials")
        raise ex

def get_api_host(cf_client, stack_name, env):
    """
    gets the api host name value to context
    Args:
        cf_client (object): boto3 client for cloud formation
        stack_name (str): cloud formation stack name to lookup
        env (str): cloudx env (values = dev, qa, prod)
    Returns:
        str: api gateway stage host name
    Raises:
        Exception: API host name not found
    """
    stack_info = {}
    try:
        stack_info = cf_client.describe_stacks(StackName=stack_name)
        LOGGER.debug("Stack info: %s", stack_info)
        for item in stack_info["Stacks"][0]["Outputs"]:
            if item["OutputKey"] == "ServiceEndpoint":
                return item["OutputValue"].replace("https://", "").replace(f"/{env}", "")
    except Exception as err:
        LOGGER.exception(err)
        LOGGER.error(f"An error occurred while getting cloudstack name {str(err)}")
        raise err

    raise Exception("API host name not found")

"""
contains behave step implementation
"""
# pylint: disable = import-error,no-name-in-module,line-too-long,C0111,W0603,W0613

import os
import sys
import json
import requests
import boto3
from hamcrest import assert_that, equal_to, has_item, greater_than, is_not
from behave import then, given, when
from utils import awsapi, helper, data_objects, api_core
from tests import logger

THISDIR = os.path.dirname(__file__) # steps/
if THISDIR not in sys.path:
    sys.path.append(THISDIR)
BDDDIR = os.path.dirname(THISDIR) # bdd/
if BDDDIR not in sys.path:
    sys.path.append(BDDDIR)
TESTSDIR = os.path.dirname(BDDDIR) # tests/
if TESTSDIR not in sys.path:
    sys.path.append(TESTSDIR)

# secret keys
SHARED_APPSYNC_SECRET_NAME = os.environ.get('shared_appsync_secret_name', 'NextBot/AppSync')

def get_ami_id(ssm_param_path, region='us-east-1'):
    """gets aws amazon official public ami image id from ssm parameter store"""
    client = boto3.client('ssm', region_name=region)
    amzn_amis = client.get_parameter(Name=ssm_param_path)
    return amzn_amis['Parameter']['Value']

def get_current_exceptions(context):
    """helper method to retrieve ami exceptions stored in appsync service"""
    appsync_conn_info = json.loads(helper.retrieve_secret(SHARED_APPSYNC_SECRET_NAME, context.region))
    account_data = api_core.get_appsync_accounts_data(
        appsync_conn_info,
        data_objects.ImageData(
            image_id=context.ami_id,
            region_name=context.region,
            account_id=context.test_account,
            vpc_id=context.vpc_id
        )
    )
    ami_exceptions = account_data.get('ami_exceptions',[])
    if not ami_exceptions:
        ami_exceptions = []
    return ami_exceptions

def invoke_api(context, method="PUT"):
    """helper method to invoke rest api service for testing"""
    logger.debug("token: %s", context.token)
    logger.debug("api-host: %s", context.api_host)
    logger.info("Invoking API")
    headers = {
        'Authorization': context.token,
        'Host': context.api_host,
        "Content-Type": "application/json"
    }
    params = {}
    kwargs = {
        'headers': headers,
        'json': params,
        'verify': False
    }
    logger.info("---------------------------------")
    logger.info("Making %s API call", method)
    logger.info("---------------------------------")
    response = requests.request(method, context.url, **kwargs)
    logger.info("---------------------------------")
    logger.info("Response: %s", response)
    logger.info("Response details: %s", response.text)
    logger.info("Response headers: %s", response.headers)
    logger.info("Response url: %s", response.url)

    context.status_code = response.status_code
    context.response_data = (json.loads(response.text))

@given(u'DELETE API /v1/accounts/{account}/regions/{region}/amis/{image}/vpcs/{vpc}/ami_exception exists')
def step_impl_given_delete_url(context, account, region, image, vpc):
    """
    Build the url with config items
    """
    ami_id = get_ami_id('/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2', context.region)
    if image == 'BAD_image':
        ami_id = "ami-324e1eacd1"
    context.ami_id = ami_id
    vpc_id = "*"
    if vpc == "vpc_id":
        vpc_id = context.vpc_id
    account_id = context.test_account
    if account == 'invalid_acc':
        account_id = 'itx-invalid'
    context.url = (
        f'{context.application_endpoint}/v1/accounts/'
        f'{account_id}/regions/{context.region}/amis/'
        f'{ami_id}/vpcs/{vpc_id}/ami_exception'
    )
    logger.info("url: %s", context.url)
    assert context.url

@given(u'PUT API /v1/accounts/<account_id>/regions/<region_name>/amis/<image_id>/vpcs/{vpc}/ami_exception exists')
def step_impl_given_put_url(context, vpc):
    """
    Build the url with config items
    """
    context.ami_id = get_ami_id('/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2', context.region)
    vpc_id = "*"
    if vpc == "vpc_id":
        vpc_id = context.vpc_id
    elif vpc == "vpc2_id":
        vpc_id = context.vpc2_id
    context.url = (
        f'{context.application_endpoint}/v1/accounts/'
        f'{context.test_account}/regions/{context.region}/amis/'
        f'{context.ami_id}/vpcs/{vpc_id}/ami_exception'
    )
    logger.info("url: %s", context.url)
    assert context.url

@given(u'valid oauth2 token for API authorization generated')
def step_impl_given_oauth(context):
    """
    Get a valid token for the put storage tags API
    """
    logger.info("Getting auth token...")
    context.token = awsapi.get_access_token(context.token_url, context.api_client_id, context.api_client_secret, context.application_scope)
    assert context.token

@given(u'VPCx account {account} is valid')
def step_impl_given_acc(context, account):
    """
    Set the valid account from the config
    """
    assert context.test_account

@given(u'VPCx account {account} does not exist')
def step_impl_given_no_acc(context, account):
    """
    Set the valid account from the config
    """
    assert context.test_account

@given(u'Region <region_name> is valid')
def step_impl_given_region(context):
    """
    Set the valid region from the config
    """
    assert context.region

@given(u'AMI <image_id> is valid')
def step_impl_given_ami(context):
    """
    Set the valid ami using default aws ssm parameter
    """
    context.ami_id = get_ami_id('/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2', context.region)
    assert context.ami_id

@given(u'VPC {vpc} is valid')
def step_impl_given_vpc(context, vpc):
    """
    Set the valid vpc from the config
    """
    if vpc == "vpc_id":
        assert context.vpc_id
    elif vpc == "vpc2_id":
        assert context.vpc2_id
    else:
        assert vpc == "*"

@given(u'Exception for the {image} exists in the accounts table - {exists}')
def step_impl_ami_exception_entry_exists(context, image, exists):
    if image == "bdd_image":
        invoke_api(context)
    ami_exceptions = get_current_exceptions(context)
    if exists == "yes":
        assert_that(ami_exceptions, has_item(f'{context.ami_id}|{context.region}|{context.vpc_id}'))
    else:
        assert_that(ami_exceptions, is_not(has_item(f'{context.ami_id}|{context.region}|{context.vpc_id}')))

@given(u'AMI exception entry exists for <image_id> + <region_name> + <account_id> + specific vpc')
def step_impl_ami_exception_exists_vpc(context):
    """
    Set the valid vpc2 from the config
    """
    ami_exceptions = get_current_exceptions(context)
    assert_that(ami_exceptions, has_item(f'{context.ami_id}|{context.region}|{context.vpc_id}'))

@given(u'AMI exception entry exists for <image_id> + <region_name> + <account_id> + wild card vpc')
def step_impl_ami_exception_exists_wildcard(context):
    """
    Set the valid vpc2 from the config
    """
    ami_exceptions = get_current_exceptions(context)
    assert_that(ami_exceptions, has_item(f'{context.ami_id}|{context.region}|*'))

@when(u'we invoke the API to add <image_id>, <region_name>, <account_id>, {vpc}')
def step_impl_invoke_vpc2(context, vpc):
    """
    Invoke the put ami-exception tags API
    """
    if vpc == '*':
        ami_id = get_ami_id('/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2', context.region)
        context.url = (
            f'{context.application_endpoint}/v1/accounts/'
            f'{context.test_account}/regions/{context.region}/amis/'
            f'{ami_id}/vpcs/*/ami_exception'
        )
        logger.info("url: %s", context.url)

    invoke_api(context)

@when(u'we invoke the API to remove {image}, {region}, {vpc} from {account}')
def step_impl_invoke_remove(context, image, region, vpc, account):
    """
    Invoke the put ami-exception tags API
    """
    invoke_api(context, "DELETE")

@then(u'API returns a status of 200')
def step_impl_then_stat_200(context):
    """
    Assert that the API response code is 200
    :param context:
    :return:
    """
    assert_that(context.status_code, equal_to(200))

@then(u'API returns a status of 404')
def step_impl_then_stat_404(context):
    """
    Assert that the API response code is 404
    :param context:
    :return:
    """
    assert_that(context.status_code, equal_to(404))

@then(u'the AMI exception is removed from AppSync Acccount table')
def step_impl_ami_exception_removed(context):
    ami_exceptions = get_current_exceptions(context)
    assert_that(ami_exceptions, is_not(has_item(f'{context.ami_id}|{context.region}|{context.vpc_id}')))

@then(u'the AMI image is added to the AppSync Acccount table for {vpc}')
def step_impl_ami_exception_added(context, vpc):
    """
    check if the ami exception exists in the appsync
    """
    if vpc == "*":
        assert_that(context.response_data.get('success'), equal_to(f"AMI added [{context.ami_id}, {context.region}, {context.test_account}, *]."))
    elif vpc == "vpc_id":
        assert_that(context.response_data.get('success'), equal_to(f"AMI added [{context.ami_id}, {context.region}, {context.test_account}, {context.vpc_id}]."))
    else:
        assert_that(context.response_data.get('success'), equal_to(f"AMI added [{context.ami_id}, {context.region}, {context.test_account}, {context.vpc2_id}]."))

@then(u'previous entry(s) AppSync Acccount table for the AMI with fine-grained VPC id are {state}')
def step_impl_ami_exception_upgraded(context, state):
    """
    check if the ami exception exists in the appsync
    """
    ami_exceptions = get_current_exceptions(context)
    logger.info("Before filter: %s", ami_exceptions)
    ami_exceptions = list(filter(
        lambda item: item.startswith(f'{context.ami_id}|{context.region}|'.lower()),
        ami_exceptions))
    logger.info("After filter: %s", ami_exceptions)

    if state == "not deleted":
        assert_that(len(ami_exceptions), greater_than(1))
    if state == "deleted":
        assert_that(len(ami_exceptions), equal_to(1))

@then(u"existing entry in AppSync Acccount table for the AMI's VPC is updated from wildcard to vpc_id")
def step_impl_ami_exception_downgraded(context):
    """
    check if the ami exception exists in the appsync
    """
    ami_exceptions = get_current_exceptions(context)
    assert_that(ami_exceptions, has_item(f'{context.ami_id}|{context.region}|{context.vpc_id}'))

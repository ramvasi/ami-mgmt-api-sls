"""
Module for common methods used for Lambda API
"""

# pylint: disable = no-name-in-module,logging-fstring-interpolation,import-error,no-self-use,broad-except,C0413,C0411

import os
import sys
import json
import logging
from utils.data_objects import Response
from utils import helper, data_objects, awsapi
from utils.exceptions import ResourceUnknownException, AccountNotFound, InvalidInputException
from cloudx_appsync_helper import appsync
from cloudx_appsync_helper.exceptions import GQLAccountNotFound

THISDIR = os.path.dirname(__file__)
if THISDIR not in sys.path:
    sys.path.append(THISDIR)
APPDIR = os.path.dirname(THISDIR)
if APPDIR not in sys.path:
    sys.path.append(APPDIR)

# Logger setup
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get('log_level', logging.WARNING))

# secret keys
SHARED_APPSYNC_SECRET_NAME = os.environ.get('shared_appsync_secret_name', 'NextBot/AppSync')

def get_appsync_accounts_data(appsync_conn_info, ami_data):
    """
    Verifies the contents of ami data
    Args:
        appsync_conn_info (dict): app sync connection info object (key, url)
        ami_data (ImageData): ami meta data dao
    Returns:
        dict: validated principal account
    Raises:
        AccountNotFound: Account '<account_id>' not found
        InvalidInputException: Region '<region_name>' is not a valid or apporved aws region
    """
    try:
        accounts_data = appsync.get_account_by_project_id(
            appsync_conn_info,
            ami_data.account_id,
            "project_id, regions, ami_exceptions")
        LOGGER.info("account info: %s", accounts_data)
    except GQLAccountNotFound as err:
        LOGGER.exception(err)
        raise AccountNotFound(f"Account '{ami_data.account_id}' not found") from err

    if not accounts_data or len(accounts_data)<=0:
        raise AccountNotFound(f"Account '{ami_data.account_id}' not found")

    filtered_accounts_data = list(filter(lambda acc: ami_data.region_name in acc.get('regions'), accounts_data))
    LOGGER.info("filtered account info: %s", filtered_accounts_data)
    if not filtered_accounts_data or len(filtered_accounts_data)<=0:
        raise InvalidInputException(f"Region '{ami_data.region_name}' is not a valid or apporved aws region")

    return filtered_accounts_data[0]

def _update_appsync_account_data(appsync_conn_info, record_id, ami_exceptions):
    """
    Use cloudx appsync lib and update appsync db
    Args:
        appsync_conn_info (dict): app sync connection info object (key, url)
        record_id (str): id of appsync record to be updated
        ami_exceptions (list(str)): list of ami exceptions
    """
    data = {
        "id": record_id,
        "ami_exceptions": ami_exceptions
    }
    return appsync.update_account(appsync_conn_info, data, "project_id, regions, ami_exceptions")

def process_ami_exception_list(ami_data, ami_exceptions):
    """
    Method generates ami exception list subject to various rules
    |  AMI  |  Region   |    VPC   |               comment                   |
    | AMI 2 | us-east-2 |     *    | exception ami for an account            |
    | AMI 3 | us-east-2 | vpc-1234 | exception ami for an account and vpc    |
    |   *   | us-west-1 | vpc-789  | exception vpc - allowed to host any AMI |
    Args:
        ami_data (ImageData): ami meta data dao
        ami_exceptions (set): list of ami exceptions
    Returns:
        list: list of processed ami exceptions added/removed/merged
    """
    LOGGER.debug("before process ami excpetion: %s", ami_exceptions)
    # if vpc is wild card
    if ami_data.vpc_id == "*":
        # # for given region, remove all ami with wildcard  (ami cannot be * if vpc is *)
        # ami_exceptions = set(filter(lambda item: not item.startswith(f'*|{ami_data.region_name}|') , ami_exceptions))
        # remove all entries for given ami and region (upgrade)
        ami_exceptions = set(
            filter(
                lambda item: not item.startswith(f'{ami_data.image_id}|{ami_data.region_name}|'.lower()),
                ami_exceptions))
    # if ami image is wild card
    elif ami_data.image_id == "*":
        # # remove all vpc with wildcard for region (vpc cannot be * if ami is *)
        # ami_exceptions = set(filter(lambda item: not item.endswith(f'{ami_data.region_name}|*') , ami_exceptions))
        # remove all entries for given vpc and region (upgrade)
        ami_exceptions = set(
            filter(
                lambda item: not item.endswith(f'{ami_data.region_name}|{ami_data.vpc_id}'.lower()),
                ami_exceptions))
    else:
        # downgrade
        ami_exceptions = set(filter(
            lambda item: (
                not item == f'*|{ami_data.region_name}|{ami_data.vpc_id}'.lower()
                and not item == f'{ami_data.image_id}|{ami_data.region_name}|*'.lower()
            ),
            ami_exceptions))
    ami_exceptions.add(f'{ami_data.image_id}|{ami_data.region_name}|{ami_data.vpc_id}'.lower())
    LOGGER.debug("after process ami excpetion: %s", ami_exceptions)
    return list(ami_exceptions)

def _process_put_exception_ami_request(request):
    """
    Method parse put exception request and update appsync account with exceptions
    Args:
        request (dict): api gateway event
    Returns:
        Response: success message as response dao
    Raises:
        InvalidInputException: Image '<image_id>' is invalid.
        InvalidInputException: VPC '<vpc_id>' is invalid.
    """
    ami_data = data_objects.unmarshall_exception_image_vars(request.path_parameters)
    LOGGER.info('ami data: %s', ami_data)

    appsync_conn_info = json.loads(helper.retrieve_secret(SHARED_APPSYNC_SECRET_NAME, 'us-east-1'))
    principal_account = get_appsync_accounts_data(appsync_conn_info, ami_data)
    LOGGER.info('principal account: %s', principal_account)

    vpciam_config = data_objects.unmarshall_vpcx_iam_vars(os.environ)
    LOGGER.info(f'vpcx iam config: {vpciam_config}')
    credentials = awsapi.get_aws_credentials_for_account(ami_data.account_id, vpciam_config)
    if "*" not in ami_data.image_id:
        try:
            if not helper.verify_ami_image_id_exists(ami_data.image_id, ami_data.region_name, credentials):
                raise InvalidInputException(f"Image '{ami_data.image_id}' is invalid.")
        except Exception as ex:
            LOGGER.exception(ex)
            raise InvalidInputException(f"Image '{ami_data.image_id}' is invalid.") from ex
    if "*" not in ami_data.vpc_id:
        try:
            if not helper.verify_vpc_id_exists(ami_data.vpc_id, ami_data.region_name, credentials):
                raise InvalidInputException(f"VPC '{ami_data.vpc_id}' is invalid.")
        except Exception as ex:
            LOGGER.exception(ex)
            raise InvalidInputException(f"VPC '{ami_data.vpc_id}' is invalid.") from ex

    ami_exceptions = principal_account.get('ami_exceptions',[])
    # The check below is added to handle None (first time) scenario and init exception list.
    # By default AppSync stores None instead of empty list.
    if not ami_exceptions:
        ami_exceptions = []
    ami_exceptions = process_ami_exception_list(ami_data, set(ami_exceptions))
    LOGGER.debug("ami excpetion: %s", ami_exceptions)

    result = _update_appsync_account_data(appsync_conn_info, principal_account.get("id"), ami_exceptions)
    LOGGER.debug("updated record: %s", result)

    return Response(200, body=json.dumps({"success":
        f"AMI added [{ami_data.image_id}, {ami_data.region_name}, {ami_data.account_id}, {ami_data.vpc_id}]."}))

def _process_delete_exception_ami_request(request):
    """
    Method parse delete ami exception request and update appsync account with exceptions
    Args:
        request (dict): api gateway event
    Returns:
        Response: success message as response dao
    Raises:
        InvalidInputException: Image '<image_id>' is invalid.
        InvalidInputException: VPC '<vpc_id>' is invalid.
    """
    ami_data = data_objects.unmarshall_exception_image_vars(request.path_parameters)
    LOGGER.info('ami data: %s', ami_data)

    appsync_conn_info = json.loads(helper.retrieve_secret(SHARED_APPSYNC_SECRET_NAME, 'us-east-1'))
    principal_account = get_appsync_accounts_data(appsync_conn_info, ami_data)
    LOGGER.info('principal account: %s', principal_account)

    ami_exceptions = principal_account.get('ami_exceptions', [])
    ami_exceptions = list(
        filter(
            lambda item: not item.startswith(f'{ami_data.image_id}|{ami_data.region_name}|{ami_data.vpc_id}'.lower()),
            ami_exceptions
        )
    )
    LOGGER.debug("ami excpetion: %s", ami_exceptions)

    result = _update_appsync_account_data(appsync_conn_info, principal_account.get("id"), ami_exceptions)
    LOGGER.debug("updated record: %s", result)

    return Response(200, body=json.dumps({"success":
        f"AMI deleted [{ami_data.image_id}, {ami_data.region_name}, {ami_data.account_id}, {ami_data.vpc_id}]."}))

def _process_unknown_resource_request(request):
    """
    Default request method. Triggered when supported resource request
    Args:
        request (dict): api gateway event
    Returns:
        None
    Raises:
        ResourceUnknownException: Resource not found [<http_method>] <request.resource>
    """
    message = f'Resource not found [{request.http_method}] {request.resource}'
    LOGGER.error(message)
    raise ResourceUnknownException(message)

def ami_mgmt_contoller(request):
    """
    Main AMI management api controller. Controller will switch the request to appropriate request
    Args:
        request (dict): api gateway event
    Returns:
        Response: success message as response dao
    """
    switcher = {
        "put+/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception":
            _process_put_exception_ami_request,
        "delete+/v1/accounts/{account_id}/regions/{region_name}/amis/{image_id}/vpcs/{vpc_id}/ami_exception":
            _process_delete_exception_ami_request
    }
    request_key = "+".join([request.http_method.lower(), request.resource.lower()])
    LOGGER.info('switch to: %s', request_key)

    func = switcher.get(request_key, _process_unknown_resource_request)
    return func(request)

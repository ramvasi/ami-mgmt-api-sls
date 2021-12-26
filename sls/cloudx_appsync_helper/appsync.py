
"""Core Cloudx AppSync helper methods"""

# pylint: disable=import-error, wrong-import-position,unused-argument,broad-except,no-name-in-module

import os
import sys
import logging
import json
import boto3

THISDIR = os.path.dirname(__file__)
APPDIR = os.path.dirname(THISDIR)
if THISDIR not in sys.path:
    sys.path.append(THISDIR)
if APPDIR not in sys.path:
    sys.path.append(APPDIR)

from sls.cloudx_appsync_helper import gql_utils as utils
from sls.cloudx_appsync_helper.exceptions import (
    GQLMissingParameter,
    GQLAccountNotFound,
    GQLException)

# Logger setting
LOG_LEVEL = 'log_level'
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get(LOG_LEVEL, logging.INFO))
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(os.environ.get(LOG_LEVEL, logging.INFO))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

def get_appsync_conn_info(secret_name='NextBot/AppSync', region_name='us-east-1'):
    """
    Returns appsync connection information
    Args:
        secret_name (str): secert manager secret name (default: NextBot/AppSync)
        region_name (str): aws region the secret is located (default: us-east-1)
    Returns:
        dict: connection object with key and url
    """
    client = boto3.client('secretsmanager', region_name)
    return json.loads(client.get_secret_value(SecretId=secret_name,
                                              VersionStage='AWSCURRENT'
                                              ).get('SecretString'))

def get_account_by_project_id(conn_info, project_id, addl_items=""):
    """
    Get account table data by project id from appsync db
    Args:
        conn_info (dict): app sync connection info object (key, url)
        account_data (dict): data object with data to be updates (id,ami_exceptions)
        addl_query_items (str): comma separated list of items to be queried
    Returns:
        list: account record objects
    Raises:
        GQLMissingParameter: Project ID parameter missing
        GQLAccountNotFound: Account not found for project <project_id>
    """
    if not project_id:
        raise GQLMissingParameter("Project ID parameter missing")
    LOGGER.info("Looking up project: %s", project_id)

    response = utils.execute_gql(
        endpoint=conn_info.get('url'),
        key=conn_info.get('key'),
        query=utils.gql_query_get_account_by_project_id(addl_items),
        variables=json.dumps({"ProjectId": project_id})
    )
    accounts = response.get("data").get("GetAccountByProjectId").get("items", [])
    if not accounts:
        raise GQLAccountNotFound(f"Account not found for project {project_id}")

    if len(accounts) > 1:
        raise GQLException(f"Multiple account records found for project {project_id}")

    return accounts

def get_ext_account_by_project_id(conn_info, project_id, items):
    """
    Get account table data by project id from appsync db
    Args:
        conn_info (dict): app sync connection info object (key, url)
        account_data (dict): data object with data to be updates (id,ami_exceptions)
        addl_query_items (str): comma separated list of items to be queried
    Returns:
        list: account record objects
    Raises:
        GQLMissingParameter: Project ID parameter missing
        GQLAccountNotFound: Account not found for project <project_id>
    """
    if not project_id:
        raise GQLMissingParameter("Project ID parameter missing")
    LOGGER.info("Looking up project: %s", project_id)

    response = utils.execute_gql(
        endpoint=conn_info.get('url'),
        key=conn_info.get('key'),
        query=utils.gql_query_get_ext_account_by_project_id(items),
        variables=json.dumps({"ProjectId": project_id})
    )
    accounts = response.get("data").get("GetAccountByProjectId").get("items", [])
    if not accounts:
        raise GQLAccountNotFound(f"Account not found for project {project_id}")

    if len(accounts) > 1:
        raise GQLException(f"Multiple account records found for project {project_id}")

    return accounts

def update_account(conn_info, account_data, addl_query_items=""):
    """
    Update account table by record id in appsync db
    Args:
        conn_info (dict): app sync connection info object (key, url)
        account_data (dict): dict data object with data to be updates (id <required>,ami_exceptions)
        addl_query_items (str): comma separated list of items to be queried post update
    Returns:
        list: Updates account and returns account object
    Raises:
        GQLException: Account not updated
    """
    if not conn_info:
        raise GQLMissingParameter("Missing AppSync connection info {key:str, url:str}")
    if not account_data:
        raise GQLMissingParameter("Missing account data object")
    if not account_data.get('id', ""):
        raise GQLMissingParameter("Missing id key in account data object")

    LOGGER.info("updating account table record id: %s", account_data.get('id'))
    response = utils.execute_gql(
        endpoint=conn_info.get('url'),
        key=conn_info.get('key'),
        query=utils.gql_query_update_account(account_data, addl_query_items)
        # variables=json.dumps(account_data)
    )
    item_data = response.get("data").get("updateAccount", "")
    if not item_data:
        raise GQLException("Account not updated")

    return item_data

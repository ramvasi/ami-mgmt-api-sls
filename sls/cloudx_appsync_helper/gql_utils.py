"""module consists of gql queries and gql utility functions"""

# pylint: disable=import-error, wrong-import-position,unused-argument,broad-except,no-name-in-module

import os
import sys
import json
import logging
import requests
from sls.cloudx_appsync_helper.exceptions import GQLException

LOG_LEVEL = 'log_level'
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get(LOG_LEVEL, logging.INFO))
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(os.environ.get(LOG_LEVEL, logging.INFO))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# reference => serverless>service_enablement>lambda>util>gql_utils
def execute_gql(endpoint, key, query, variables=None):
    """
    Makes rest api call to appsync service to execute gql query
    Args:
        endpoint (str): app sync connection endpoint
        key (str): api authorization key
        query (str): gql query to executed
        variables (any): optional variables for gql query
    Returns:
        dict: json object of rest api response body
    Raises:
        GQLException: GQL query failed. [<response.status_code>-<error_type>] <error_msg>
    """
    headers = {
        'Content-Type': "application/json",
        'x-api-key': key,
        "Authorization": key,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Expose-Headers': '*',
    }
    data = {
        'query': query
    }
    if variables:
        data['variables'] = variables
    response = requests.post(endpoint, json=data, headers=headers)

    logger.debug("gql exec reponse[%s]: %s", response.status_code, response.json())
    if response.json().get("errors", []) or response.status_code != 200:
        error_type = response.json().get("errors", [])[0].get('errorType', 'Unknown')
        error_msg = response.json().get("errors", [])[0].get('message', 'Unknown error')
        raise GQLException(f"GQL query failed. [{response.status_code}-{error_type}] {error_msg}")
    return response.json()

# reference => serverless>service_enablement>lambda>get_account>app>get_account_handler
def gql_query_get_account_by_project_id(addl_query_items=""):
    """
    Helper method to generate 'get account by project' gql query
    Args:
        addl_query_items (str): comma separated list of items to be queried
    Returns:
        str: gql to query account table
    """
    query_items = '\n\t\t'.join(addl_query_items.replace(',', ' ').split())
    gql_query = '''
        query GetAccountByProjectId($ProjectId:String){{
            GetAccountByProjectId(project_id: $ProjectId){{
            items{{
                id
                {query_items}
            }}
            }}
        }}
    '''.format(query_items=query_items)
    logger.debug("get project account gql : %s", gql_query)
    return gql_query

def gql_query_get_ext_account_by_project_id(query_items):
    """
    Helper method to generate 'get account by project with nested fields' gql query
    Args:
        query_items (str): items to query in GQL SDL format
    Returns:
        str: gql to query account table
    """
    gql_query = '''
        query GetAccountByProjectId($ProjectId:String){{
            GetAccountByProjectId(project_id: $ProjectId){{
                {query_items}
            }}
        }}
    '''.format(query_items=query_items)
    logger.debug("get project account gql : %s", gql_query)
    return gql_query

# reference => serverless>service_enablement>lambda>update_account>app>update_account_handler
def gql_query_update_account(input_data, addl_query_items=""):
    """
    Helper method to generate 'update account' gql mutation
    Args:
        input_data (dict): object of account table items (required item: id)
        addl_query_items (str): comma separated list of items to be queried post update
    Returns:
        str: gql query account table mutation
    Raises:
        GQLMissingParameter: Missing id key in account data object
    """
    if input_data and not input_data.get("id"):
        raise GQLException("Missing id key in account data object")
    input_items = ""
    for k in input_data:
        input_items += f'{k}: {json.dumps(input_data.get(k))}\n\t\t'
    query_items = '\n\t\t'.join(addl_query_items.replace(',', ' ').split())
    gql_query = '''
        mutation UpdateAccount{{
            updateAccount(input:{{
                {input_items}
            }}){{
                id
                {query_items}
            }}
        }}
    '''.format(input_items=input_items, query_items=query_items)
    logger.debug("update account gql : %s", gql_query)
    return gql_query

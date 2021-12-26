"""
This module contains the core lambda function code various AMI exception API requests.

This file uses environment variables in place of config; thus
sddcapi_boot_dir is not required.
"""

# pylint: disable=bad-option-value,import-error,logging-format-interpolation,broad-except,too-many-statements,C0413,W1203,R1703,R0914

import os
import sys
import json
import logging
import botocore.exceptions

# append the path of the parent directory
THISDIR = os.path.dirname(__file__)
if THISDIR not in sys.path:
    sys.path.append(THISDIR)
APPDIR = os.path.dirname(THISDIR)
if APPDIR not in sys.path:
    sys.path.append(APPDIR)

from utils import awsapi, api_core, data_objects
from utils.data_objects import Response
from utils.exceptions import ResourceUnknownException, InvalidInputException, AccountNotFound, AuthorizationException

# Logger setup
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get('log_level', logging.WARNING))

def handler(event, context):
    """
    Main lambda handler
    Args:
        event (dict): lambda event object from API gateway
        context (dict): request context (not used)
    Returns:
        dict: api gateway proxy compatible response object
    """
    LOGGER.info(f'event: {event}')
    response = {}
    try:
        ldap = data_objects.unmarshall_ldap_env_vars(os.environ)
        LOGGER.info(f'ldap config: {ldap}')
        awsapi.verify_request_authorization(event, ldap)

        request = data_objects.unmarshall_api_gateway_event(event)
        LOGGER.info(f'request: {request}')

        response = api_core.ami_mgmt_contoller(request)
    except InvalidInputException as err:
        LOGGER.exception(f'{type(err).__name__}: {err}')
        response = Response(400, body=json.dumps({
            'error': f'{err}'
        }))
    except AuthorizationException as err:
        LOGGER.exception(err)
        response = Response(401, body=json.dumps({
            'error': f'{err}'
        }))
    except botocore.exceptions.ClientError as err:
        LOGGER.exception(f'{type(err).__name__}: {err}')
        response = Response(500, body=json.dumps({
            'error': f'{type(err).__name__}: {err}'
        }))
    except ResourceUnknownException as err:
        LOGGER.exception(f'{err}')
        response = Response(404, body=json.dumps({
            'error': f'{err}'
        }))
    except AccountNotFound as err:
        LOGGER.exception(f'{err}')
        response = Response(404, body=json.dumps({
            'error': f'{err}'
        }))
    except Exception as err:
        LOGGER.exception(f'{type(err).__name__}: {err}')
        response = Response(500, body=json.dumps({
            'error': f'{type(err).__name__}: {err}'
        }))

    LOGGER.info(f'response: {response}')
    return response.__dict__

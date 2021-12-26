"""
this module contains behave framework function implementation
"""
# pylint:disable=no-name-in-module,import-error, C0413, C0411

import os
import sys
import boto3
import configparser

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '')))

THISDIR = os.path.dirname(__file__)  # bdd/
# STEPDIR = os.path.dirname(THISDIR + '/steps/')  # steps/
TESTDIR = os.path.dirname(THISDIR)  # tests/
LAMBDADIR = os.path.dirname(TESTDIR)  # ami-exception/
SLSDIR = os.path.dirname(LAMBDADIR)  # sls/
APPDIR = os.path.dirname(SLSDIR)  # ami_mgmt/
SERVERLESSDIR = os.path.dirname(APPDIR)  # serverless_2/
ROOTDIR = os.path.dirname(SERVERLESSDIR)  # awsapi/

sys.path.insert(0, THISDIR)
sys.path.insert(0, TESTDIR)
sys.path.insert(0, LAMBDADIR)
sys.path.insert(0, SLSDIR)
sys.path.insert(0, APPDIR)
sys.path.insert(0, SERVERLESSDIR)
sys.path.insert(0, ROOTDIR)

from sls.utils import awsapi, helper
from tests import logger
# from tests import config, logger, shared_config

def before_all(context):
    """
    This method runs before all
    Args:
        context:
    Returns:
    """
    # environment variables for app

    logger.info("======================")
    logger.info("IN BEFORE")
    logger.info("======================")

    config = configparser.ConfigParser()
    config.read(["config/main_config.ini", f"config/{os.environ.get('ENV', 'dev')}_config.ini"])

    context.environment = os.environ.get('ENV', 'dev')
    context.token_url = config['main']['token_url']
    context.region = config['main']['region']
    context.application_endpoint = config['oauth2']['application_vpc_endpoint']
    context.application_scope = config['oauth2']['application_scope']
    context.application_account = config['main']['admin_account']
    context.test_account = config['behave']['account']
    context.test_account_id = config['behave']['account_id']

    context.stack_name = f"clx-awsapi-ami-mgmt-{context.environment}"
    context.api_host = awsapi.get_api_host(
        boto3.client('cloudformation', context.region),
        context.stack_name,
        context.environment
    )

    context.api_client_id = config['behave']['jenkins_client_id']
    context.api_client_secret = helper.retrieve_secret(config['behave']['jenkins_secret_name'])

    # Get VPC, subnet and security group id
    context.vpc_id = config['behave']['vpc_id']
    context.vpc2_id = config['behave']['vpc2_id']

def after_scenario(context, scenario):
    """
    This method is called after each scenario
    :param context:
    :param scenario:
    :return:
    """

    logger.info("======================")
    logger.info("CLEANING UP SCENARIO")
    logger.info("======================")

def after_all(context):
    """
    Cleanup all the resources created by the BDD for testing
    """
    logger.info("======================")
    logger.info("CLEANING ALL SCENARIO")
    logger.info("======================")

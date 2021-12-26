"""
base init file
"""
# pylint:disable=wrong-import-position,wrong-import-order, import-error, W0703

import os
import sys
import logging

LOG_LEVEL = 'log_level'

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get(LOG_LEVEL, logging.ERROR))
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(os.environ.get(LOG_LEVEL, logging.ERROR))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# from entconfig import entconfigmgr
# # sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../ami-mgmt')))
# try:
#     _config_mgr = entconfigmgr.get_ent_config_mgr()
#     config = _config_mgr.get_app_config('ami-mgmt')
#     shared_config = _config_mgr.get_shared_config()
# except Exception as err:
#     print(f'{type(err).__name__}: {err}')

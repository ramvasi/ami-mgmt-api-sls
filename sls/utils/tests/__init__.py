"""
Init test module libraries
"""

import os
import sys
import configparser

# LOG_LEVEL = 'log_level'
# logger = logging.getLogger(__name__)
# logger.setLevel(os.environ.get(LOG_LEVEL, logging.ERROR))
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(os.environ.get(LOG_LEVEL, logging.ERROR))
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

config = configparser.ConfigParser()
config.read([f"config/{os.environ.get('ENV', 'dev')}_config.ini"])

if 'env' in config:
    for k in config['env']:
        os.environ[k] = config['env'].get(k)

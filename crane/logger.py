import logging
import logging.handlers
import logging.config

from crane.config import config


logger = logging.getLogger('Crane')
handler = logging.handlers.SysLogHandler(address='/dev/log')
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

if config['general']['loglevel'] == 'DEBUG':
    logger.setLevel(logging.DEBUG)
elif config['general']['loglevel'] == 'INFO':
    logger.setLevel(logging.INFO)
elif config['general']['loglevel'] == 'WARNING':
    logger.setLevel(logging.WARNING)
elif config['general']['loglevel'] == 'ERROR':
    logger.setLevel(logging.ERROR)
elif config['general']['loglevel'] == 'CRITICAL':
    logger.setLevel(logging.CRITICAL)

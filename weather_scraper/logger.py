import logging
from pathlib import Path
import colorlog
import sys
import os

LOG_LVL_MAP = {
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'err': logging.ERROR,
    'error': logging.ERROR,
    'inf': logging.INFO,
    'info': logging.INFO,
}


def init_logger(dunder_name,
                root=None,
                log_level=logging.DEBUG) -> logging.Logger:
    """Sets-up logging behavior. Env variable `log_level` overrides the logging
    level.

    Args:
        dunder_name (str): name of the source of the logging.
        root (Pathlike, optional): If logging to file is required, must be 
            other than `None`. Defaults to None.
        log_level (_type_, optional): logging.DEBUG, ERROR, etc. Defaults to logging.DEBUG.

    Returns:
        logging.Logger: _description_
    """

    log_format = (
        '%(asctime)s - '
        '%(name)s - '
        '%(funcName)s - '
        '%(levelname)s - '
        '%(message)s'
    )
    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{log_format}'
    )
    colorlog.basicConfig(format=colorlog_format)
    logger = logging.getLogger(dunder_name)

    logger.setLevel(log_level)

    log_level_env = os.getenv('log_level')
    if log_level_env and log_level_env.lower() in LOG_LVL_MAP:
        logger.setLevel(LOG_LVL_MAP[log_level_env.lower()])

    handler = logging.StreamHandler(sys.stdout)

    if root:
        root = Path(root)
        log_filename = root / Path('app.log')
        root.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_filename, mode='a',
                                      encoding=None, delay=False)

    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

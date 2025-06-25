# src/logger_config.py

import logging

def setup_logging(level=logging.ERROR, log_file=None):
    """
    Configure global logging for the application.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO, logging.ERROR)
        log_file: Optional file path to log to a file instead of console
    """
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    if log_file:
        logging.basicConfig(
            level=level,
            format=log_format,
            filename=log_file,
            filemode='a'
        )
    else:
        logging.basicConfig(
            level=level,
            format=log_format
        )

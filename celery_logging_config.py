import logging
import os
from math import log 
from celery.signals import after_setup_logger, after_setup_task_logger

def _configure(logger: logging.Logger) -> None:
    logger.handlers.clear()
    logger.setLevel(os.getenv("CELERY_LOG_LEVEL", "INFO").upper())
    logger.propagate = False 

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    ))
    logger.addHandler(handler)

@after_setup_logger.connect
def setup_root_logger(logger, *args, **kwargs):
    _configure(logger)

@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    _configure(logger)
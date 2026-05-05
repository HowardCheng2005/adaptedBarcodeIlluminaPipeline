"""
This file contains all functions related to managing fiels and durectories for the pipeline
"""

import glob
import logging
import os
from datetime import datetime


def create_log(status):
    """
    Create log file in logs directory.
    :param status: if True, create log file with current date and time; else create test.log
    :return: logger object
    """
    if not os.path.exists(os.path.join(os.getcwd(), "logs")):
        os.mkdir("logs")

    if status:
        logger = logging.getLogger(__name__)
        log_filename = os.path.join(os.getcwd(), "logs", datetime.now().strftime(f"%Y-%m-%d_%H:%M_{__file__.split('/')[-1]}.log"))
        logging.basicConfig(filename=log_filename,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)
    else:
        logger = logging.getLogger(__name__)
        log_filename = os.path.join(os.getcwd(), "logs", datetime.now().strftime("test.log"))
        logging.basicConfig(filename=log_filename,
                            format='%(asctime)s - [%(filename)s] - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)

    return logger


def create_dir(parent_dir, dir_name):
    """
    Create directory.
    :param parent_dir: parent directory
    :param dir_name: new directory name
    :return: new directory path
    """
    out_dir = os.path.join(parent_dir, dir_name)

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    return str(os.path.join(parent_dir, dir_name))


def get_files(dir, pattern):
    """
    Get files in directory.
    :param dir: directory to search in
    :param pattern: pattern to search for files
    :return: a list of files
    """
    return sorted([file for file in glob.glob(os.path.join(dir, pattern))])

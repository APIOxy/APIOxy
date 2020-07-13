"""
This module contains functions which are shared across multiple APIOxy modules.
As such, it should not import any other ARC module (specifically ones that use the logger defined here)
to avoid circular imports.

VERSION is the full APIOxy version, using `semantic versioning <https://semver.org/>`_.
"""

import datetime
import logging
import os
import shutil
import subprocess
import sys
import time
import warnings
import yaml
from typing import Dict, List, Optional, Tuple, Union

from arc.settings import arc_path, servers, default_job_types
from arc.common import is_str_float, is_str_int, read_yaml_file, save_yaml_file


logger = logging.getLogger('apioxy')

VERSION = '0.1.0'

apioxy_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # absolute path to the APIOxy folder
PROJECTS_BASE_PATH = os.path.join(apioxy_path, 'Projects')


def initialize_log(log_file: str,
                   project: str,
                   project_directory: Optional[str] = None,
                   verbose: int = logging.INFO,
                   ) -> None:
    """
    Set up a logger for APIOxy.

    Args:
        log_file: The log file name.
        project: A name for the project.
        project_directory: The path to the project directory.
        verbose: Specify the amount of log text seen.
    """
    # backup and delete an existing log file if needed
    if project_directory is not None and os.path.isfile(log_file):
        if not os.path.isdir(os.path.join(project_directory, 'log_and_restart_archive')):
            os.mkdir(os.path.join(project_directory, 'log_and_restart_archive'))
        local_time = datetime.datetime.now().strftime("%H%M%S_%b%d_%Y")
        log_backup_name = 'apioxy.old.' + local_time + '.log'
        shutil.copy(log_file, os.path.join(project_directory, 'log_and_restart_archive', log_backup_name))
        os.remove(log_file)

    logger.setLevel(verbose)
    logger.propagate = False

    # Use custom level names for cleaner log output
    logging.addLevelName(logging.CRITICAL, 'Critical: ')
    logging.addLevelName(logging.ERROR, 'Error: ')
    logging.addLevelName(logging.WARNING, 'Warning: ')
    logging.addLevelName(logging.INFO, '')
    logging.addLevelName(logging.DEBUG, '')
    logging.addLevelName(0, '')

    # Create formatter and add to handlers
    formatter = logging.Formatter('%(levelname)s%(message)s')

    # Remove old handlers before adding ours
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])

    # Create console handler; send everything to stdout rather than stderr
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(verbose)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Create file handler
    fh = logging.FileHandler(filename=log_file)
    fh.setLevel(verbose)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    log_header(project=project)

    # ignore Paramiko and cclib warnings:
    warnings.filterwarnings(action='ignore', module='.*paramiko.*')
    warnings.filterwarnings(action='ignore', module='.*cclib.*')
    logging.captureWarnings(capture=False)


def get_logger() -> logger:
    """
    Get the APIOxy logger (avoid having multiple entries of the logger).
    """
    return logger


def log_header(project: str,
               level: int = logging.INFO,
               ) -> None:
    """
    Output a header containing identifying information about APIOxy to the log.

    Args:
        project: The APIOxy project name to be logged in the header.
        level: The desired logging level.
    """
    logger.log(level, f'APIOxy execution initiated on {time.asctime()}')
    logger.log(level, '')
    logger.log(level, '###############################################################')
    logger.log(level, '#                                                             #')
    logger.log(level, '#                         APIOxy                              #')
    logger.log(level, '#                                                             #')
    logger.log(level, f'#   Version: {VERSION}{" " * (10 - len(VERSION))}                                       #')
    logger.log(level, '#                                                             #')
    logger.log(level, '###############################################################')
    logger.log(level, '')
    logger.log(level, 'Cite this work as:')
    logger.log(level, 'Oscar Haoyang Wu, Alon Grinberg Dana, Duminda Ranasinghe')
    logger.log(level, '')

    # Extract HEAD git commit from ARC
    head, date = get_git_commit()
    branch_name = get_git_branch()
    if head != '' and date != '':
        logger.log(level, 'The current git HEAD for APIOxy is:')
        logger.log(level, f'    {head}\n    {date}')
    if branch_name and branch_name != 'master':
        logger.log(level, f'    (running on the {branch_name} branch)\n')
    else:
        logger.log(level, '\n')
    logger.info(f'Starting project {project}')


def log_footer(execution_time: str,
               level: int = logging.INFO,
               ) -> None:
    """
    Output a footer for the log.

    Args:
        execution_time: The overall execution time for ARC.
        level: The desired logging level.
    """
    logger.log(level, '')
    logger.log(level, f'Total execution time: {execution_time}')
    logger.log(level, f'ARC execution terminated on {time.asctime()}')


def string_representer(dumper: yaml.Dumper,
                       data: str,
                       ) -> yaml.Dumper.represent_scalar:
    """
    Add a custom string representer to use block literals for multiline strings.

    Args:
        dumper: A YAML dumper.
        data: A data string.

    Returns:
        YAML dumper.represent_scalar.
    """
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar(tag='tag:yaml.org,2002:str', value=data, style='|')
    return dumper.represent_scalar(tag='tag:yaml.org,2002:str', value=data)


def globalize_paths(file_path: str,
                    project_directory: str,
                    ) -> str:
    """
    Rebase all file paths in the contents of the given file on the current project path.
    Useful when restarting an ARC project in a different folder or on a different machine.

    Args:
        file_path: A path to the file to check.
                   The contents of this file will be changed and saved as a different file.
        project_directory: The current project directory to rebase upon.

    Returns:
        A path to the respective file with rebased absolute file paths.
    """
    modified = False
    new_lines = list()
    if project_directory[-1] != '/':
        project_directory += '/'
    with open(file_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        new_line = globalize_path(line, project_directory)
        modified = modified or new_line != line
        new_lines.append(new_line)
    if modified:
        base_name, file_name = os.path.split(file_path)
        file_name_splits = file_name.split('.')
        new_file_name = '.'.join(file_name_splits[:-1]) + '_globalized.' + str(file_name_splits[-1])
        new_path = os.path.join(base_name, new_file_name)
        with open(new_path, 'w') as f:
            f.writelines(new_lines)
        return new_path
    else:
        return file_path


def globalize_path(string: str,
                   project_directory: str,
                   ) -> str:
    """
    Rebase an absolute file path on the current project path.
    Useful when restarting an ARC project in a different folder or on a different machine.

    Args:
        string: A string containing a path to rebase.
        project_directory: The current project directory to rebase upon.

    Returns:
        A string with the rebased path.
    """
    if '/calcs/Species/' in string or '/calcs/TSs/' in string and project_directory not in string:
        splits = string.split('/calcs/')
        prefix = splits[0].split('/')[0]
        new_string = prefix + project_directory + 'calcs/' + splits[-1]
        return new_string
    return string


def is_notebook() -> bool:
    """
    Check whether ARC was called from an IPython notebook.

    Returns:
        ``True`` if ARC was called from a notebook, ``False`` otherwise.
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter

def str_to_float_fail_none(value: str) -> Union[None, float]:
    return float(value) if is_str_float(value) else None

def str_to_int_fail_none(value: str) -> Union[None, int]:
    return int(value) if is_str_int(value) else None

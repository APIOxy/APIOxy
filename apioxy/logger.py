"""
apioxy logger module

Using a custom logger to avoid interference with RMG's / ARC's loggers.
"""

import datetime
import os
import shutil
import time
from typing import Optional

from arc.common import get_git_branch, get_git_commit, time_lapse

from t3.logger import Logger as T3Logger

from apioxy.common import VERSION, apioxy_path


class Logger(T3Logger):
    """
    The APIOxy Logger class.

    Args:
        project (str): The project name.
        project_directory (str): The project directory path.
        verbose (Optional[int]): The logging level, optional. 10 - debug, 20 - info, 30 - warning.
                                 ``None`` to avoid logging to file.
        t0 (float): Initial time when the project was spawned.

    Attributes:
        project (str): The project name.
        project_directory (str): The project directory path.
        verbose (Optional[int]): The logging level, optional. 10 - debug, 20 - info, 30 - warning.
                                 ``None`` to avoid logging to file.
        t0 (float): Initial time when the project was spawned.
        log_file (str): The path to the log file.
    """

    def __init__(self,
                 project: str,
                 project_directory: str,
                 verbose: Optional[int],
                 t0: float,
                 ):

        self.project = project
        self.project_directory = project_directory
        self.verbose = verbose
        self.t0 = t0
        self.log_file = os.path.join(self.project_directory, 'APIOxy.log')

        if os.path.isfile(self.log_file):
            if not os.path.isdir(os.path.join(os.path.dirname(self.log_file), 'log_archive')):
                os.mkdir(os.path.join(os.path.dirname(self.log_file), 'log_archive'))
            local_time = datetime.datetime.now().strftime("%H%M%S_%b%d_%Y")
            log_backup_name = 'APIOxy.' + local_time + '.log'
            shutil.copy(self.log_file, os.path.join(os.path.dirname(self.log_file), 'log_archive', log_backup_name))
            os.remove(self.log_file)

        self.log_header()

    def log_header(self):
        """
        Output a header to the log.
        """
        self.log(f'T3 execution initiated on {time.asctime()}\n\n'
                 f'################################################################\n'
                 f'#                                                              #\n'
                 f'#                            APIOxy                            #\n'
                 f'#                                                              #\n'
                 f'#                        Version: {VERSION}{" " * (10 - len(VERSION))}                   #\n'
                 f'#                                                              #\n'
                 f'################################################################\n\n',
                 level='always')

        # Extract HEAD git commit from T3
        head, date = get_git_commit(path=apioxy_path)
        branch_name = get_git_branch(path=apioxy_path)
        if head != '' and date != '':
            self.log(f'The current git HEAD for APIOxy is:\n'
                     f'    {head}\n    {date}',
                     level='always')
        if branch_name and branch_name != 'master':
            self.log(f'    (running on the {branch_name} branch)\n',
                     level='always')
        else:
            self.log('\n', level='always')
        self.log(f'Starting project {self.project}', level='always')

    def log_footer(self):
        """
        Output a footer to the log.
        """
        execution_time = time_lapse(self.t0)
        self.log(f'\n\n\nTotal APIOxy execution time: {execution_time}', level='always')
        self.log(f'APIOxy execution terminated on {time.asctime()}\n', level='always')

"""
APIOxy - A self-improving tool to predict oxidative stability of active pharmaceutical ingredients
"""

import logging
import os

from apioxy.common import read_yaml_file
from apioxy.main import APIOxy
from apioxy.parsing import parse_command_line_arguments


def main() -> None:
    """
    The main APIOxy executable function
    """

    args = parse_command_line_arguments()
    input_file = args.file
    input_file_directory = os.path.abspath(os.path.dirname(args.file))
    input_dict = read_yaml_file(path=input_file, project_directory=input_file_directory)
    try:
        input_dict['project']
    except KeyError:
        print('A project name must be provided in the input file!')

    try:
        input_dict['apioxy_settings']
    except KeyError:
        print('The "apioxy_settings" block is missing in the input file!')

    # if project directory is not given in the input file, use the directory of the input file instead
    apioxy_project_directory = input_dict['apioxy_settings'].get('project_directory', str())
    apioxy_project_directory = apioxy_project_directory if apioxy_project_directory else input_file_directory
    input_dict['project_directory'] = apioxy_project_directory

    verbose = logging.INFO
    if args.debug:
        verbose = logging.DEBUG
    elif args.quiet:
        verbose = logging.WARNING
    input_dict['verbose'] = input_dict['verbose'] if 'verbose' in input_dict else verbose

    apioxy_object = APIOxy(**input_dict)
    apioxy_object.execute()


if __name__ == '__main__':
    main()

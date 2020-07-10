from argparse import ArgumentParser, Namespace
from typing import List, Optional


def add_command_line_arguments(parser: ArgumentParser,
                               ) -> None:
    """
    Add command line arguments to an ArgumentParser.

    Args:
        parser: An ArgumentParser object.
    """
    # Positional arguments
    parser.add_argument('file',
                        metavar='FILE',
                        type=str,
                        nargs=1,
                        help='an APIOxy input file describing the job to execute',
                        )

    # Optional arguments
    # Options for controlling the amount of information printed to the console
    # By default a moderate level of information is printed; you can either
    # ask for less (quiet), more (verbose), or much more (debug)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d',
                       '--debug',
                       action='store_true',
                       help='print debug information',
                       )
    group.add_argument('-q',
                       '--quiet',
                       action='store_true',
                       help='only print warnings and errors',
                       )


def parse_command_line_arguments(command_line_args: Optional[List[str]] = None,
                                 ) -> Namespace:
    """
    Parse command-line arguments.

    Args:
        command_line_args: A list of strings of commands to parse.

    Returns:
        A Namespace object containing the parsed arguments.
    """
    parser = ArgumentParser()
    add_command_line_arguments(parser)
    args = parser.parse_args(command_line_args)
    # If multiple input files are provided, only use the first one
    args.file = args.file[0]

    return args

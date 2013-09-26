"""
econo.cli -- CLI tools for the econo economic simulation
"""
import logging; logger = logging.getLogger(__name__)
from argparse import ArgumentParser, FileType
from yaml import safe_load as load_yaml

VERSION = 0.1

def main():
    """
    Tool for generating or simulating economies
    """
    parser = ArgumentParser(version=VERSION, description=main.__doc__)
    subparsers = parser.add_subparsers()

    # Handle the new command
    subparser = subparsers.add_parser('new', help=cmd_new.__doc__)
    subparser.set_defaults(func=cmd_new)

    # Handle the run command
    subparser = subparsers.add_parser('run', help=cmd_run.__doc__)
    subparser.add_argument('-s', '--steps', type=int, default=10000,
            help='Number of steps to simulate (default %(default)d)')
    subparser.add_argument('description-file', type=FileType, nargs='+',
            help='One or more YAML files containing economic descriptions to be'
                 'read in order')
    subparser.set_defaults(func=cmd_run)

    # Parse options
    args = parser.parse_args()
    args.func(args)

def cmd_new(args):
    """
    Generate a new economic description
    """
    pass

def cmd_run(args):
    """
    Simulate an economy for a specified number of steps
    """
    description = {}
    for desc_file in args.description_file:
        with desc_file:
            description.update(load_yaml(desc_file))

    # TODO: Validate data structures
    # TODO: Reconstruct economy and run it

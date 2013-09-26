"""
econo.cli -- CLI tools for the econo economic simulation
"""
import logging; logger = logging.getLogger(__name__)
from argparse import ArgumentParser

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
    pass

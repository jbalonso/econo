"""
econo.cli -- CLI tools for the econo economic simulation
"""
import logging; logger = logging.getLogger(__name__)
from argparse import ArgumentParser, FileType
from yaml import (safe_load as load_yaml, dump as save_yaml)
from sys import exit

from .unit import (parse_careers, parse_units, step_time, save_careers,
        save_units)
from .market import (parse_market, save_market)

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

    # Initialize logging
    logging.basicConfig(level=logging.DEBUG)

    # Run command
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

    # Extract major data substructures
    config_system = description.get('system', None)
    config_market = description.get('market', None)
    config_careers = description.get('careers', None)
    config_units = description.get('units', None)

    # Validate the system data substructure
    try:
        if not isinstance(config_system, dict):
            raise ValueError('system configuration is not a dictionary')
        if not isinstance(config_system['t'], int):
            raise ValueError('iteration number t is not an integer')
        if not isinstance(config_system['interest_rate'], float):
            raise ValueError('interest rate is not a float')
        if not isinstance(config_system['min_balance'], float):
            raise ValueError('minimum balance is not a float')
        if not isinstance(config_system['max_age'], int):
            raise ValueError('maximum age is not an integer')
        if not isinstance(config_system['eat_every'], int):
            raise ValueError('eat interval is not an integer')
        if not isinstance(config_system['spawn_every'], int):
            raise ValueError('spawn interval is not an integer')
    except (KeyError, ValueError) as exc:
        logger.error(exc.message, exc_info=True)
        exit(1)
    t_0 = config_system['t']
    rate = config_system['rate']
    min_balance = config_system['min_balance']

    # Parse the data substructures
    market = parse_market(config_market)
    careers = parse_careers(config_careers, market)
    units = parse_units(config_units, careers)

    # Run the economy
    for t in xrange(t_0, t_0 + args.steps):
        step_time(t, market, careers, units, rate, min_balance=min_balance,
                max_age=max_age, eat_every=eat_every, spawn_every=spawn_every)

    # Save the results
    config_system['t'] = t
    results = dict(system=config_system,
                   market=save_market(market),
                   careers=save_careers(careers),
                   units=save_units(units))
    print save_yaml(results)

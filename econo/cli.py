"""
econo.cli -- CLI tools for the econo economic simulation
"""
import logging; logger = logging.getLogger(__name__)
from argparse import ArgumentParser, FileType
from yaml import (safe_load as load_yaml, dump as save_yaml)
from sys import exit

from .unit import (parse_careers, parse_units, step_time, save_careers,
        save_units, parse_unit_ids, save_unit_ids)
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
    subparser.add_argument('-i', '--report-interval', type=int, default=100,
            help='Number of steps between reports (default %(default)d)')
    subparser.add_argument('description_file', type=FileType('r'), nargs='+',
            help='One or more YAML files containing economic descriptions to be'
                 'read in order')
    subparser.set_defaults(func=cmd_run)

    # Parse options
    args = parser.parse_args()

    # Initialize logging
    logging.basicConfig(level=logging.INFO)

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
    logger.info('parsing input files...')
    for desc_file in args.description_file:
        data = load_yaml(desc_file)
        if data is None:
            data = {}
        description.update(data)
        desc_file.close()
    logger.info('input files parsed')

    # Extract major data substructures
    config_system = description.get('system', None)
    config_market = description.get('market', None)
    config_careers = description.get('careers', None)
    config_units = description.get('units', None)
    config_unit_ids = description.get('next_unit_ids', None)

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

        # Parse the data substructures
        market = parse_market(config_market)
        careers = parse_careers(config_careers, market)
        units = parse_units(config_units, careers)
        parse_unit_ids(config_unit_ids)
    except (KeyError, ValueError) as exc:
        logger.error(exc.message, exc_info=True)
        exit(1)

    t_0 = config_system['t']
    rate = config_system['interest_rate']
    min_balance = config_system['min_balance']
    max_age = config_system['max_age']
    eat_every = config_system['eat_every']
    spawn_every = config_system['spawn_every']

    # Run the economy
    from .market import ask_at
    for t in xrange(t_0, t_0 + args.steps):
        step_time(t, market, careers, units, rate, min_balance=min_balance,
                max_age=max_age, eat_every=eat_every, spawn_every=spawn_every)
        if (t % args.report_interval) == 0:
            logger.info('market: %r',
                        {k: ask_at(market, k) for k in market})

            res_stats = {k: '%(bought)d bot, %(sold)d sld'
                            % market[k] for k in market}
            logger.info('market: %r', res_stats)
            for career, career_rec in careers.items():
                logger.info('t=%06d: career %s: %r',
                            t, career, career_rec['stats'])

    # Save the results
    config_system['t'] = t
    results = dict(system=config_system,
                   market=save_market(market),
                   careers=save_careers(careers),
                   units=save_units(units),
                   next_unit_ids=save_unit_ids())
    print save_yaml(results)

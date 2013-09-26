"""
econo.unit -- classes and operations for representing units (people)

A Unit's state is a dictionary with the following structure:

    age: (integer) the number of time steps the unit has existed
    busy: (integer) the number of time steps the unit must wait before
            performing another operation
    career: (string) key into the careers dictionary
    balance: (float) the total currency balance the unit posesses
    name: (string) a unique identifier for the unit
"""
import logging; logger = logging.getLogger(__name__)
from collections import namedtuple, defaultdict
from copy import deepcopy

from .market import sell, buy, price_op, ask_at

# The Op class takes three components: costs, products, and time
# - name: friendly name for the operation
# - costs: dictionary mapping resource names to quantities consumed
# - products: dictionary mapping resource names to quantities produced
# - time: number of time steps consumed by unit
Op = namedtuple('Op', 'name costs products time')

def choose_op(market, ops, rate, balance, min_balance, max_time):
    """
    Given a market, a set of valid operations, an interest rate, and a starting
    balance, determine the most profitable operation to perform
    """
    # Determine the no-op profit
    noop_profit = 0.0
    if balance < 0.0:
        shortfall = -balance
        noop_profit = -(shortfall * rate)

    # Determine the most profitable operation
    best_op = None
    best_rate = noop_profit
    for op in ops:
        profit_rate, _, low_balance = price_op(market, op, rate, balance)
        if low_balance < min_balance:
            continue
        elif op.time > max_time:
            continue
        elif profit_rate > best_rate:
            best_op = op
            best_rate = profit_rate

    return (best_op, best_rate)

def perform_op(market, unit_state, op):
    """
    Given a market, a unit state, an operation, and a precomputed profit,
    update the market and unit state to reflect the performance of an option
    """
    # Update balance
    unit_state['balance'] += profit

    # Operation complete if performing noop
    if op is None:
        return

    # Purchase resources
    for resource, count in op.costs.iteritems():
        buy(market, resource, qty=count)

    # Sell resources
    for resource, count in op.products.iteritems():
        sell(market, resource, qty=count)

    # Spend time
    unit_state['busy'] += op.time

NEXT_UNIT_ID = defaultdict(lambda: 0)
def new_name(career):
    """
    Generate a new, hopefully unique name for a unit
    """
    global NEXT_UNIT_ID
    NEXT_UNIT_ID[career] += 1
    name = '%s_%04d' % (career, NEXT_UNIT_ID[career])
    return name

def spawn_unit(t, careers, units, parent):
    """
    Add a new unit to the units dictionary, assigning it the currently most
    lucrative career
    """
    career = max(careers.keys(), key=lambda k:
            careers[k]['stats']['avg_earnings'])
    name = new_name(career)
    units[name] = dict(age=0, busy=0, career=career, balance=0, name=name)
    logger.info('t=%60d: %r gives birth to %r', t, parent, name)
    return name

def step_time(t, market, careers, units, rate, min_balance=-100, max_age=1000,
        eat_every=100, spawn_every=200):
    """
    """
    # Iterate over all units in order of balance
    unit_list = [(k, v) for k, v in units.items()]
    unit_list.sort(key=lambda x: x[1]['balance'], reverse=True)
    for key, unit_state in unit_list:
        # Eat if necessary
        if (unit_state['age'] % eat_every) == 0:
            cost = ask_at(market, 'food')
            if (unit_state['balance'] - cost) < min_balance:
                logger.warn('t=%60d: unit %(name)r (age %(age)d) starved', t,
                        unit_state)
                units.pop(key)
            else:
                unit_state['balance'] -= cost
                buy(market, 'food')
                spawn_unit(careers, units, key)

        # Spawn if appropriate and able
        if (unit_state['age'] % spawn_every) == 0:
            cost = ask_at(market, 'babykit')
            if (unit_state['balance'] - cost) < min_balance:
                logger.warn('t=%60d: unit %(name)r (age %(age)d) could not'
                            ' spawn', t, unit_state)
                units.pop(key)
            else:
                unit_state['balance'] -= cost
                buy(market, 'babykit')
                spawn_unit(t, careers, units, key)

        # Choose and perform an operation
        if unit_state['busy'] == 0:
            ops = careers[unit_state['career']]['ops']
            balance = unit_state['balance']
            max_time = max_age - unit_stage['age']
            op = choose_op(market, ops, rate, balance, min_balance, max_time)
            perform_op(market, unit_state, op)
        else:
            unit_state['busy'] -= 1

        # Age the unit
        unit_state['age'] += 1
        if unit_state['age'] >= max_age:
            logger.info('t=%60d: unit %r dies of old age', t, key)

    # Compute avg_earnings per career and other aggregate stats
    for career_rec in careers.values():
        career_rec['stats']['total_balance'] = 0.0
        career_rec['stats']['total_age'] = 0
        career_rec['stats']['population'] = 0
    for key, unit_state in unit_list:
        career = unit_state['career']
        careers[career]['stats']['total_balance'] += unit_state['balance']
        careers[career]['stats']['total_age'] += unit_state['age']
        careers[career]['stats']['population'] += 1
    for career, career_rec in careers.items():
        career_rec['stats']['avg_earnings'] = (
            career_rec['stats']['total_balance'] /
            career_rec['stats']['total_age'])
        logger.info('t=%60d: career %s: %r', t, career, career_rec['stats'])

def parse_careers(config_careers, market):
    """
    Convert a dictionary describing careers into an appropriate family of data
    structures, including Op objects
    """
    # Initialize output structure
    careers = {}

    # Make sure the input is a dictionary
    if not isinstance(config_careers, dict):
        raise ValueError('careers configuration is not a dictionary')

    # Process each career
    for career, config_rec in config_careers.items():
        # Start building a new record
        logger.debug('building %r career', career)
        rec = careers.setdefault(career, {})
        rec['stats'] = {}
        rec['ops'] = []

        # Copy over statistics
        if 'stats' in config_rec:
            rec['stats'] = config_rec['stats']

        # Convert operations
        if not isinstance(config_rec['ops'], dict):
            raise ValueError('careers.ops is not a dictionary')
        for op_name, config_op in config_rec['ops'].items():
            op = Op(op_name, config_op['costs'], config_op['products'],
                    config_op['time'])

            # Make sure all resources are in the market
            for resource in set(op.costs.keys()) + set(op.products.keys()):
                if resource not in market:
                    raise ValueError('... resource %r used to %r not found in'
                                     ' market' % (resource, op.name))

            # Record the operation
            logger.debug('... can %r', op.name)
            rec['ops'].append(op)

    return careers

def save_careers(careers):
    """
    Rewrite careers structure into a format that can be serialized
    """
    # Initialize output structure
    config_careers = {}

    # Process each career
    for career, career_rec in careers.items():
        # Start building a new record
        logger.debug('saving %r career', career)
        rec = config_careers.setdefault(career, {})
        rec['stats'] = career_rec['stats']
        rec['ops'] = {}

        # Convert operations
        for op in career_rec['ops']:
            op_rec = rec['ops'].setdefault(op.name, {})
            op_rec['costs'] = op.costs
            op_rec['products'] = op.products
            op_rec['time'] = op.time
            logger.debug('... with operation %r', op.name)

    return config_careers

def parse_units(config_units, careers):
    """
    Convert a dictionary describing units (people) into an appropriate family of
    data structures. This mostly involves validation and setting defaults.
    """
    # The output is the same as the input, initially
    units = config_units

    # Iterate over each unit
    logger.debug('validating units')
    for u_name, u_rec in units.iteritems():
        logger.debug('... %s', u_name)
        for param in ['age', 'busy', 'career', 'balance']:
            if param not in u_rec:
                raise ValueError('unit %r lacking a(n) %r' % (u_name, param))
        u_rec['name'] = u_name
        if u_rec['career'] not in careers:
            raise ValueError('unit %r has career %r, but that career is unknown'
                    % (u_name, u_rec['career']))

    return units

def save_units(units):
    """
    Rewrite units structure into a format that can be serialized. This mostly
    involves stripping out redundant name data.
    """
    # Perform a deep copy on the input structure
    config_units = deepcopy(units)

    # Strip out excess name strucutres
    for u_name, u_rec in config_units.iteritems():
        u_rec.pop('name')

    return config_units

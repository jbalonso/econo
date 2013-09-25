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

from .market import sell, buy, price_op

# The Op class takes three components: costs, products, and time
# - costs: dictionary mapping resource names to quantities consumed
# - products: dictionary mapping resource names to quantities produced
# - time: number of time steps consumed by unit
Op = namedtuple('Op', 'costs products time')

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
    career = max(careers.keys(), key=lambda k: careers[k]['avg_earnings'])
    name = new_name(career)
    units[name] = dict(age=0, busy=0, career=career, balance=0, name=name)
    logger.info('t=%60d: %r gives birth to %r', t, parent, name)
    return name

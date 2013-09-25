"""
econo.unit -- classes and operations for representing units (people)

A Unit's state is a dictionary with the following structure:

    age: (integer) the number of time steps the unit has existed
    busy: (integer) the number of time steps the unit must wait before
            performing another operation
    career: (string) key into the careers dictionary
    balance: (float) the total currency balance the unit posesses
"""
import logging; logger = logging.getLogger(__name__)
from collections import namedtuple

from .market import sell, buy, price_op

# The Op class takes three components: costs, products, and time
# - costs: dictionary mapping resource names to quantities consumed
# - products: dictionary mapping resource names to quantities produced
# - time: number of time steps consumed by unit
Op = namedtuple('Op', 'costs products time')

def choose_op(market, ops, rate, balance, min_balance):
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
        elif profit_rate > best_rate:
            best_op = op
            best_rate = profit_rate

    return (best_op, best_rate)

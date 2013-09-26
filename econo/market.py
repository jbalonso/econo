"""
econo.market -- market simulation routines

A 'market' is a dictionary mapping resource names to dictionaries of the
following form:

    type: [linear|exponential]
    delta: (integer) # the net number of purchases from initial conditions
    rate: (float) # the per-delta cost change of buying/selling the resource
    initial: (float) the cost of the resource at delta=0
    
"""
import logging; logger = logging.getLogger(__name__)

def bid_at(market, resource, qty=1):
    """
    Compute the sale value of a resource
    """
    # Extract the market record for the resource
    assert resource in market, "Resource must be in the market"
    assert qty >= 0, "Quantity must be non-negative"
    rec = market[resource]
    type_name, initial, delta, rate = (res['type'], res['initial'],
            res['delta'], res['rate'])

    # Handle pricing for linear and exponential resources differently
    price = 0.0
    for step in xrange(qty):
        if res['type'] == 'linear':
            price += max(0.0, initial + (delta - 1) * rate)
        elif res['type'] == 'exponential':
            price += initial * (rate ** (delta - 1))
        else:
            assert False, "Resource type must be linear or exponential."
        delta -= 1

    return price

def sell(market, resource, qty=1):
    """
    Update a market with the sale of a resource into it
    """
    # Extract the market record for the resource
    assert resource in market, "Resource must be in the market"
    assert qty >= 0, "Quantity must be non-negative"
    rec = market[resource]
    rec['delta'] -= qty


def ask_at(market, resource, qty=1):
    """
    Compute the purchase cost of a resource
    """
    # Extract the market record for the resource
    assert resource in market, "Resource must be in the market"
    assert qty >= 0, "Quantity must be non-negative"
    rec = market[resource]
    type_name, initial, delta, rate = (res['type'], res['initial'],
            res['delta'], res['rate'])

    # Handle pricing for linear and exponential resources differently
    price = 0.0
    for step in xrange(qty):
        if res['type'] == 'linear':
            price += max(0.0, initial + delta * rate)
        elif res['type'] == 'exponential':
            price += initial * (rate ** delta)
        else:
            assert False, "Resource type must be linear or exponential."
        delta += 1

    return price

def buy(market, resource, qty=1):
    """
    Update a market with the purchase of a resource from it
    """
    # Extract the market record for the resource
    assert resource in market, "Resource must be in the market"
    assert qty >= 0, "Quantity must be non-negative"
    rec = market[resource]
    rec['delta'] += qty

def price_op(market, op, rate, balance):
    """
    Compute the per time step profit (loss) on an operation given a market,
    operation, starting balance, and a per time step interest rate.
    """
    # Compute the total cost of resource dependencies
    cost = 0.0
    for resource, count in op.costs.iteritems():
        cost += ask_at(market, resource, qty=count)

    # Compute the loan amount
    if cost > balance:
        loan = max(0.0, cost - balance)
        loan *= (1.0 + rate) ** op.time
        cost += loan - (cost - balance)

    # Compute the earnings amount
    earnings = 0.0
    for resource, count in op.products.iteritems():
        earnings += bid_at(market, resource, qty=count)

    # Compute the profit
    profit = earnings - cost

    # Compute the earnings rate and minimum balance
    return ((profit / op.time), profit, balance - cost)

def parse_market(config_market):
    """
    Convert a dictionary describing market conditions into an appropriate family
    of data structures. This mostly involves validation.
    """
    # The output is the same as the input
    if not isinstance(config_market, dict):
        raise ValueError('market configuration is not a dictionary')
    market = config_market

    # Make sure that food and babykits are present
    if 'food' not in market:
        raise ValueError('Market must contiain food')
    if 'babykits' not in market:
        raise ValueError('Market must contain babykits')

    # Make sure that each resource is fully specified
    logger.debug('validating resources')
    for resource, rec in market.items():
        logger.debug('... %s', resource)
        if rec['type'] not in ['linear', 'exponential']:
            raise ValueError('resource type neither linear nor exponential')
        if not isinstance(rec['delta'], int):
            raise ValueError('resource delta is not an integer')
        if not isinstance(rec['initial'], float):
            raise ValueError('initial resource value is not a float')
        if not isinstance(rec['rate'], float):
            raise ValueError('resource value model is not a float')

    return market

def save_market(market):
    """
    Rewrite market structure into a format that can be serialized
    """
    return market

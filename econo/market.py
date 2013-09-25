"""
econo.market -- market simulation routines

A 'market' is a dictionary mapping resource names to dictionaries of the
following form:

    type: [linear|exponential]
    delta: (integer) # the net number of purchases from initial conditions
    rate: (float) # the per-delta cost change of buying/selling the resource
    initial: (float) the cost of the resource at delta=0
    
"""

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

"""
econo.unit -- classes and operations for representing units (people)
"""
import logging; logger = logging.getLogger(__name__)
from collections import namedtuple

# The Op class takes three components: costs, products, and time
# - costs: dictionary mapping resource names to quantities consumed
# - products: dictionary mapping resource names to quantities produced
# - time: number of time steps consumed by unit
Op = namedtuple('Op', 'costs products time')

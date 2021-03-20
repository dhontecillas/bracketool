"""Create first round of clashes for bracket type competitions.

Functions here can be shared for single elimination, and double
elimination competition configurations.
"""

import math

from bracketool.domain import Clash

def _assign_byes(bracket_slots, begin, end, num_byes):
    """Distribute byes so competitors that have a bye in the
    first round have less chances to fight each other.
    """
    if num_byes > 1:
        mid = begin + (end - begin) // 2
        mid_byes = num_byes // 2
        _assign_byes(bracket_slots, begin, mid, mid_byes)
        _assign_byes(bracket_slots, mid, end, num_byes - mid_byes)
    elif num_byes == 1:
        bracket_slots[begin].is_bye = True

def generate_first_round_clashes(num_participants):
    """Generates the minimum number of clashes that fits the amount of
    competitors.

    Populate the 'byes' (the 'phantom' losers that will pair with competiors
    that will pass automatically to the next round).
    """
    if num_participants < 0:
        raise ValueError('number of participants must be 0 or greater')
    elif num_participants < 2:
        return []
    first_round_slots = (1 << int(math.ceil(math.log(num_participants, 2))))
    num_clashes = first_round_slots // 2
    num_byes = first_round_slots - num_participants
    bracket_slots = [Clash() for _ in range(num_clashes)]
    if num_byes == 0:
        return bracket_slots
    _assign_byes(bracket_slots, 0, len(bracket_slots), num_byes)
    return bracket_slots


def brackets_max_depth_distance(bracket_slots):
    """Returns the number of rounds a competitor must pass to win."""
    return int(math.log(len(bracket_slots), 2)) + 1


def brackets_depth_distance(clashes, idx_a, idx_b):
    """Given two slot indices (each clash has two slots) from the
    first round, returns the number of rounds each one must pass
    to face each other.
    """
    n_clashes = len(clashes)
    if idx_a < 0 or idx_a >= n_clashes:
        raise IndexError('idx_a index out of range')
    if idx_b < 0 or idx_b >= n_clashes:
        raise IndexError('idx_b index out of range')
    if idx_a == idx_b:
        return 1
    max_distance = int(math.log(n_clashes, 2)) + 1
    s = n_clashes // 2
    while s > 0 and idx_a // s == idx_b // s:
        max_distance = max_distance - 1
        s = s // 2
    return max_distance

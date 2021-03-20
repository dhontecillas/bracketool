"""
    This module contains generic creation of bracket
    slots functions.
"""

import math
import random
import time

from bracketool.domain import Clash, ClashGenerator
from bracketool.brackets import generate_first_round_clashes
from bracketool.teambrackets import create_reserved_teams_bracket_clashes
from bracketool.teambrackets import clashes_team_count
from bracketool.pairings import PairingsGenerator


class SingleElimination(object):
    def __init__(self):
        self.rounds = []
        self.all = []

    def round(self, idx):
        return self.rounds[idx]


class SingleEliminationGen(ClashGenerator):
    """Creates single elimination brackets."""

    def __init__(self,
                 use_three_way_final=True,
                 third_place_clash=True,
                 use_teams=True,
                 use_rating=True,
                 random_seed=None):
        if random_seed is None:
            random_seed = time.time()
        self.rnd = random.Random(random_seed)
        self.use_three_way_final = use_three_way_final
        self.use_teams = use_teams
        self.use_rating = use_rating
        self.team_pairing_count = {}

    def _generate_threeway_final(self, clashes):
        # TODO: Implement the three way final
        return clashes


    def generate(self, competitor_list, team_pairing_count=None):
        rseed = self.rnd.randint(0, 1 << 31)
        pg = PairingsGenerator(use_teams=self.use_teams,
                               use_rating=self.use_rating,
                               random_seed=self.rnd.randint(0, 1 << 31))
        clashes = pg.generate(competitor_list, team_pairing_count)
        if self.use_three_way_final and len(clashes) == 2 and \
                (clashes[0].is_bye or clashes[1].is_bye):
            return self._generate_threeway_final(competitor_list)
        # TODO build the rest of clashes based on the config
        res = SingleElimination()
        res.rounds.append(clashes)
        res.all.extend(clashes)
        # iterate to build next round clashes:
        last_round = clashes
        while len(last_round)  > 1:
            num_nr = len(last_round) // 2
            next_round = [Clash() for _ in range(num_nr)]
            res.rounds.append(next_round)
            res.all.extend(next_round)
            num_all = len(res.all)
            for nr in range(num_nr):
                idx = num_all - 3 * num_nr + (nr * 2)
                to_idx = num_all - num_nr + nr
                res.all[idx].winner_to = to_idx
                res.all[idx+1].winner_to = to_idx
            last_round = next_round
        # TODO: check if we must insert a round previous to the last one
        # to decide the third and fourth place
        return res

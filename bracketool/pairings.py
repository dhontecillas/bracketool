"""
    This module contains generic creation of bracket
    slots functions.
"""

import math
import random
import time

from bracketool.brackets import brackets_depth_distance
from bracketool.brackets import generate_first_round_clashes
from bracketool.domain import Clash, ClashGenerator
from bracketool.teambrackets import clashes_team_count
from bracketool.teambrackets import create_reserved_teams_bracket_clashes


class PairingsGenerator(object):
    """Creates single elimination brackets."""

    def __init__(self, use_teams=True, use_rating=True, random_seed=None):
        if not random_seed:
            random_seed = time.time()
        self.rnd = random.Random(random_seed)
        self.use_teams = use_teams
        self.use_rating = use_rating

    def _find_competitor_clash_options(self, competitor, reservations, clashes):
        """Find the available clash options for a competitor, based on
        reservations made for a team.

        :param competitor: A competitor
        :param reservations: List of team reservations for each clash:
            [[team_a, team_b], [team_c,], [], [team_b,]]
            The length of reservation matches MUST match the length of the
            first round clashes.
            If there are no reservations, it MUST be a list of empty lists.
        :param clashes: List of Clashes for the all the rounds.

        :returns: a list of indices where a competitor can be placed.
        """
        options = []
        # find if we have reserved spots for this team:
        team_count = clashes_team_count(reservations)
        if competitor.team in team_count:
            for idx, reserv in enumerate(reservations):
                if competitor.team in reserv and clashes[idx].has_spot():
                    options.append(idx)
            if options:
                return options
        # if we could not find a reserved spot, use a free spot
        for idx, reserv in enumerate(reservations):
            if len(reserv) == 2:
                # skip full reseved
                continue
            elif len(reserv) == 1:
                # skip if there is one reservation, and only one spot left
                if clashes[idx].is_bye:
                    continue
                if clashes[idx].competitor_a is not None:
                    continue
            if clashes[idx].has_spot():
                options.append(idx)
        return options

    def _assign_clash(self, competitor, clashes, clash_idx, reservations,
                      team_pairing_count):
        clash = clashes[clash_idx]
        clash.add_competitor(competitor)
        if reservations and competitor.team in reservations[clash_idx]:
            # remove the reservations, because we are assigning it
            reservations[clash_idx].remove(competitor.team)
        if not clash.has_spot() and not clash.is_bye and \
                team_pairing_count is not None:
            team_a = clash.competitor_a.team
            team_b = clash.competitor_b.team
            if team_a and team_b:
                pt = (min(team_a, team_b), max(team_a, team_b))
                cnt = team_pairing_count.setdefault(pt, 0) + 1
                team_pairing_count[pt] = cnt

    def _further_from_others(self, options, clashes):
        opt_distances = []
        for opt_idx in options:
            opt_distances.append(
                (sum([brackets_depth_distance(clashes, opt_idx, cl_idx)
                      for cl_idx in range(len(clashes))
                      if clashes[cl_idx].competitor_a]
                     ),
                 opt_idx)
            )
        opt_distances.sort()
        return opt_distances[-1][1]

    def _assign_by_rating(self, clashes, competitor_list, reservations,
                          team_pairing_count):
        """Sort competitors by rating, and tries to put them as separate
        as possible, respecting team.
        """
        # TODO: do we really need team count for something ?:
        team_count = clashes_team_count(reservations)
        sorted_clist = sorted(
                competitor_list,
                key=lambda comp: (-comp.rating, -team_count[comp.team]))
        for idx, comp in enumerate(sorted_clist):
            options = self._find_competitor_clash_options(
                    comp, reservations, clashes)
            if not options:
                # TODO: Should we raise an exception?
                continue
            f_idx = self._further_from_others(options, clashes)
            self._assign_clash(comp, clashes, f_idx,
                               reservations, team_pairing_count)
            # This would be the naive option of alternating :
            # cheaper in computing costs but less fair
            #self._assign_clash(comp, clashes, options[-(idx % 2)],
            #                   reservations, team_pairing_count)

    def _assign_by_random(self, clashes, competitor_list, reservations,
                          team_pairing_count):
        for idx, comp in enumerate(competitor_list):
            options = self._find_competitor_clash_options(
                    comp, reservations, clashes)
            self._assign_clash(comp, clashes, self.rnd.choice(options),
                               reservations, team_pairing_count)

    def generate(self, competitor_list, team_pairing_count=None):
        if team_pairing_count is None:
            team_paiting_count = dict()
        assign_single_competitor_teams = not self.use_rating
        if self.use_teams:
            clashes, reservations = create_reserved_teams_bracket_clashes(
                competitor_list, team_pairing_count, rnd=self.rnd,
                assign_single_competitor_teams=assign_single_competitor_teams)
        else:
            clashes = generate_first_round_clashes(len(competitor_list))
            reservations = [list() for _ in clashes]
        if not clashes:
            return clashes
        if self.use_rating:
            self._assign_by_rating(clashes, competitor_list, reservations,
                                   team_pairing_count)
        else:
            self._assign_by_random(clashes, competitor_list, reservations,
                                   team_pairing_count)
        return clashes

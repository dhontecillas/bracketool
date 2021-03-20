""" Reserve slots for teams.
    This module reserve slots for teams that have
    several competitors in the same brackets.

    In order to keep track of already existing
    team pairings it uses a dictionary: team_pairing_count.

    Is a dictionary of ordered
    tuples (min, max), with the count of times
    that those two teams are matched (min, can not
    be 0, as it is an empty slot).
"""

from collections import defaultdict, Counter
from bracketool.domain import Competitor, Clash
from bracketool.brackets import generate_first_round_clashes
from bracketool.brackets import brackets_max_depth_distance
from bracketool.brackets import brackets_depth_distance


import math
import random



def assign_team_to_clash(clashes, reservations, clash_idx, team,
                         team_pairing_count=None):
    """
    Assigns a slot to a team and updates the team pairing
    counts.

    The clash must not be fully reserved or it will raise an IndexError
    exception.
    """
    reserv = reservations[clash_idx]
    if len(reserv) == 2:
        raise IndexError('No empty space in clash idx %d' % clash_idx)
    elif len(reserv) == 1 and team_pairing_count is not None:
        other_team = reserv[0]
        pt = (min(other_team, team), max(other_team, team))
        cnt = team_pairing_count.setdefault(pt, 0) + 1
        team_pairing_count[pt] = cnt
    elif clashes[clash_idx].is_bye:
        bye_cnt = team_pairing_count.setdefault((None, team), 0) + 1
        team_pairing_count[(None, team)] = bye_cnt
    reserv.append(team)


def shuffle_teams_sorted_by_slots(teams_with_required_slots, rnd):
    """Sort the teams by number of slots required, and inside the list
    of those with the same required slots, randomizes the order using rnd.

    :param dict teams_with_required_slots: mapping of team ids to
        number of competitors

    :returns list: the teams sorted by number of competitors
    """
    d = defaultdict(list)
    # group teams by count:
    for team, count in teams_with_required_slots.items():
        d[count].append(team)
    res = []
    for key in sorted(d.keys(), reverse=True):
        rnd.shuffle(d[key])
        res.extend(d[key])
    return res


def rate_clash_for_team(reservations, clashes, clash_idx, team,
                        team_pairing_count):
    """
    Gives a rating number for that spot.
    A smaller number for better spots, and bigger number
    for worse ones.

    Best spot -> not pairing
    Depending on the number of already paired
    Bye is better than pairing again with the same team
    Worse spot -> pairing with same team


    complexity: O(n)
    """
    clash = clashes[clash_idx]
    reserv = reservations[clash_idx]
    if len(reserv) == 2 or (len(reserv) == 1 and clash.is_bye):
        # there is no place in this clash, already reserved
        return None

    same_team_factor = len(clashes) * len(clashes) * 4
    rating = 0
    if team in reserv:
        # special penalization to face a member of the same team:
        rating = pow(same_team_factor, 127)

    if clash.is_bye:
        rating += team_pairing_count.get((None, team), 0)
    # this converts this function in quadratic complexity but gives
    # more precise ratings
    mdd = brackets_max_depth_distance(clashes)
    for other_idx, other_reserv in enumerate(reservations):
        d = brackets_depth_distance(clashes, other_idx, clash_idx)
        for other_team in other_reserv:
            pt = (min(other_team, team), max(other_team, team))
            penalty = team_pairing_count.get(pt, 0)
            if other_team == team:
                penalty = penalty + same_team_factor
            rating = rating + (mdd + 1 - d) * penalty
    return rating


def reserve_slots_for_team(reservations, clashes, team, required_slots,
                           team_pairing_count, rnd):
    """
    Assign the slots for the members of a team.
    """
    ratings = []
    for _ in range(required_slots):
        ratings = [(rate_clash_for_team(reservations, clashes, idx, team,
                                        team_pairing_count), idx)
                   for idx in range(len(clashes))]
        ratings = [(rate, idx) for rate, idx in ratings if rate is not None]
        ratings.sort()
        assign_team_to_clash(clashes, reservations, ratings[0][1], team,
                             team_pairing_count)


def reserve_team_slots(clashes, competitors, team_pairing_count, rnd=None,
                       assign_single_competitor_teams=True):
    """
    :param clashes: the list of first round clashes
    :param competitors: the list of competitors
    :param team_pairing_count: a dict, counting the number of times that
        one team has already been paired with each other team.
    :param rnd: a random object to select how teams with same number
        of slots are ordered.
    :param assign_single_competitor_teams: if set to true, it takes into
        account the team_pairing_count_param to reduce the number
        of same team pairings. If not, those empty spots can later be
        assigned using the competitor rating.

    :returns: list of team reservations for each clash:
        [[team_a, team_b], [team_c,], [], [team_b,]]
    """
    # we need to put first the teams with more people first, but
    # also some sort of randomness among the ones that have the same
    # number of people
    reservations = [list() for _ in clashes]
    if rnd is None:
        rnd = random.Random()
        rnd.seed()
    teams_with_required_slots = Counter([comp.team for comp in competitors
                                         if comp.team is not None])
    sorted_teams = shuffle_teams_sorted_by_slots(teams_with_required_slots, rnd)
    for team in sorted_teams:
        cnt = teams_with_required_slots[team]
        if cnt == 1 and not assign_single_competitor_teams:
            return reservations
        reserve_slots_for_team(reservations=reservations,
                               clashes=clashes,
                               team=team,
                               required_slots=cnt,
                               team_pairing_count=team_pairing_count,
                               rnd=rnd)
    return reservations


def create_reserved_teams_bracket_clashes(competitors,
                                          team_pairing_count=None,
                                          rnd=None,
                                          assign_single_competitor_teams=True):
    """
        Initialize the brackets with the number of participants
        in the tournament.

        Creates the empty brackets with byes filled.

        It reserves slots for teams, but does not assign the
        slots to individuals.

        Filling of the team slots with team members must
        be accomplished with other class, that can take into
        account: ranking, previous matches with the same
        competitor, etc ...

    :param competitors: A list of competitors `bracketool.domain.Competitor`
    :param team_pairing_count: a map that counts the number of times
        that two teams have already faced each other. Can be used to
        add more variability, if we have other brackets where the
        same teams participate. Can be None, if we don't care about
        other brackets.
    :param rnd: The random.Random object use to shuffle teams that have
        the same number of competitors
    :param assign_single_competitor_teams: To reserve spots for teams
        that only have one competitor (Setting it to False, would
        allow more flexibility to assign competitor by other properties
        like the rank).

    :returns: a list of clashes with non assigned competitors, and
        the list of team reservations.
    """
    clashes = generate_first_round_clashes(len(competitors))
    # create a temporary track of how team pairing would be distributed,
    # but real team_pairing_count is updated when competitors are
    # assigned
    if team_pairing_count is None:
        pairing_count = {}
    else:
        pairing_count = dict(team_pairing_count)
    team_reservations = reserve_team_slots(
            clashes, competitors, pairing_count, rnd,
            assign_single_competitor_teams)
    return clashes, team_reservations


def clashes_team_count(team_reservations):
    return Counter([team for reserv in team_reservations for team in reserv])

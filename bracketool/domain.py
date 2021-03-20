"""Definition of entities for bracket definitions."""

class Competitor(object):
    """Competitor information required to place it in a clash."""

    def __init__(self, name, team, rating):
        """
        :param name: unique identifier for the competitor
        :param team: unique identifier for the team
        :param rating: integer with how good is the competitor
            (higher is better)
        """
        self.name = name
        self.team = team
        self.rating = rating

    def __repr__(self):
        return 'Competitor<{}, {}, {}>'.format(
                self.name, self.team, self.rating)

    def __str__(self):
        return 'Competitor<{}, {}, {}>'.format(
                self.name, self.team, self.rating)


class Clash(object):
    """Clash information.

    Has slots for two competitors (competitor_a, and competitor_b).

    There is a flag to mark if this is a 'bye' clash (a direct
    pass for the only assigned competitor)

    There are two members that holds the indices for the clases
    where the winner (winnter_to) and the loser (loser_to) advance.
    """
    def __init__(self, competitor_a=None, competitor_b=None,
                 winner_to=None, loser_to=None):
        self.competitor_a = competitor_a
        self.competitor_b = competitor_b
        self.winner_to = winner_to
        self.loser_to = loser_to
        self.is_bye = False

    def has_spot(self):
        return self.competitor_a is None or \
            (self.competitor_b is None and not self.is_bye)

    def add_competitor(self, competitor):
        if self.competitor_a is None:
            self.competitor_a = competitor
        elif self.competitor_b is None and not self.is_bye:
            self.competitor_b = competitor
        else:
            raise ValueError("Clash does not have spot")

    def __repr__(self):
        return 'Clash<{}, {}>'.format(str(self.competitor_a),
                                      str(self.competitor_b))

    def __str__(self):
        return 'Clash<{}, {}>'.format(str(self.competitor_a),
                                      str(self.competitor_b))


class ClashGenerator(object):
    """Interface declaration for any brackets / clash organization
    class."""

    def __init__(self):
        pass

    def generate(self, competitor_list):
        """Generates the clash organization."""
        pass

    def round(self, num_round):
        """Get a list of clashes that belongs to the given round."""
        pass

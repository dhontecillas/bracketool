# Brackets generation tool

Under [MIT License](LICENSE)

The bracketool library allows you to generate brackets
for competitions, with [seeding](https://en.wikipedia.org/wiki/Seed_%28sports%29)
and taking into account same team competitors.

## A **slot**, a **clash**, and **bye**

A competitor **slot** contains the following info:

- Competitor Name
- Team
- Ranking

![Competitor Slot](./docs/images/slot.png)

Every **clash** has two slots. But a slot can also by filled
with a **bye**, that is a 'no compete' slot (so the competitor
in the other slot has a direct pass to the next round).


## Same team competitors

In some competitive events (like martial arts, for example),a team can
have several competitors in the same category. If that
is not taken into account, team mates could be placed in near
slots, and they have to face each other in the first rounds:

![Brackets without taking into account team members](./docs/images/no_teams_distance.png)

But taking into account the teams, those competitors can be placed as far
as possible, reducing the chances of having clashes of same team members:

![Brackets taking into account team members](./docs/images/teams_distance.png)


## Seeding

Seeding allows to also make strong competitors (those ones with a higher
rating) to face each other in later rounds.

This is how brackets would look without taking into account seeding:

![Brackets without seeding](./docs/images/no_seeding_distance.png)

And this would be a better bracket generation to make the highest ranked
competitor as far as possible.

![Brackets with seeding](./docs/images/seeding_distance.png)


# Installation

```
pip install bracketool
```

# Examples


```python
from bracketool.single_elimination import SingleEliminationGen
from bracketool.domain import *

se = SingleEliminationGen(
        use_three_way_final=False,
        third_place_clash=True,
        use_rating=True,
        use_teams=True,
        random_seed=42)

clist = [
    Competitor("A Comp", "1 Team", 2000),
    Competitor("B Comp", "1 Team", 1500),
    Competitor("C Comp", "1 Team", 1000),
    Competitor("D Comp", "2 Team", 2020),
    Competitor("E Comp", "2 Team", 1520),
    Competitor("F Comp", "3 Team", 1930),
    Competitor("G Comp", "4 Team", 2040),
]

output = se.generate(clist)

from pprint import pprint
pprint(output.rounds[0])
```

# Implementation structure

## [single_elimination.py](./bracketool/single_elimination.py)

This file defines a `SingleEliminationGen` class, that prepares
a full structure of clashes (not only the first round ones, but
also empty clashes to be filled with the results of previous
outcomes).

## [pairings.py](./bracketool/pairings.py)

This file contains `PairingsGenerator` in charge of creating the first round of
pairings.

## [domain.py](./bracketool/domain.py)

Contains the basic data structures for the logic.

- Competitor: Basics information for a participant in
    a championship, competition, league, etc..

- Clash: representation of a clash

- ClashGenerator: defines a basic interface to
    clash generators


## [brackets.py](./bracketool/brackets.py)

Contains the basic logic to deal with brackets:

- generate clashes with assigned `byes`
- functions to compute minimum number of clashes to
    get to the final, and the distance in clasehes
    between to classes.


## [teambrackets.py](./bracketool/teambrackets.py)

Used to reseve spots in brackets for members of the same
team.


## [elorating.py](./bracketool/elorating.py)

Functions to compute new ELO rating based on the outcomes
of a given clash.

## Reference links


References about different kind of bracket generations:

- [Single Elimination Tournament](https://en.wikipedia.org/wiki/Single-elimination_tournament)
- [Double Elimination Tournament](https://en.wikipedia.org/wiki/Double-elimination_tournament)
- [Round Robin tournament](https://en.wikipedia.org/wiki/Round-robin_tournament)
- [Seed (sports)](https://en.wikipedia.org/wiki/Seed_(sports)

- [Tournament knockout](https://en.wikipedia.org/wiki/Tournament#Knockout)

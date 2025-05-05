"""
``cricket_rnn.framework.ball``
==============================

"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from cricket_rnn.framework import Batter, Bowler, RealBatter, RealBowler
import cricket_rnn.loaders.cricsheet as cs

if TYPE_CHECKING:
    from . import RealInning, RealMatch, RealOver

BOWLING_WICKET_MODES = [
    cs.KindValues.BOWLED,
    cs.KindValues.LBW,
    cs.KindValues.CAUGHT,
    cs.KindValues.CAUGHT_AND_BOWLED,
    cs.KindValues.STUMPED,
    cs.KindValues.HIT_WICKET
]


@dataclass(eq=False, slots=True)
class Wicket:
    """
    Base class for any object that represents a wicket in a cricket match.
    Stores information about the mode of dismissal and any players involved.

    """

    mode: str
    batter: str
    bowler: str
    fielders: dict[str, bool] = field(default_factory=dict)


class RealWicket(Wicket):
    """
    Represents a wicket in an existing cricket match.
    
    """

    __slots__ = ['data']

    def __init__(self, data: cs.WicketsDict, bowler: str) -> None:
        self.data = data

        kwargs = {
            'mode': data[cs.WicketsKeys.KIND],
            'batter': data[cs.WicketsKeys.PLAYER_OUT],
            'fielders': {
                fielder_data[cs.FieldersKeys.NAME]: cs.FieldersKeys.SUBSTITUTE in fielder_data
                for fielder_data in data.get(cs.WicketsKeys.FIELDERS, [])
            }
        }

        super().__init__(bowler=bowler, **kwargs)


@dataclass(eq=False, kw_only=True, slots=True)
class Ball:
    """
    Base class for any object that represents a delivery in a cricket match.
    Stores information about the state of the match at that particular point in
    time (a snapshot of inning and player statistics).

    """

    index: int
    abs_index: int
    index_str: str
    batter: Batter
    non_striker: Batter
    bowler: Bowler
    value: str
    runs: int
    batting_runs: int
    boundary: bool
    no_balls: int
    wides: int
    leg_byes: int
    byes: int
    penalty: int
    dismissals: list[Wicket]
    score: str = ''
    pship: str = ''
    bowling_extras: int = field(init=False)
    fielding_extras: int = field(init=False)
    extras: int = field(init=False)
    bowling_runs: int = field(init=False)
    bowling_wickets: int = field(init=False)
    wickets: int = field(init=False)

    def __abs__(self) -> int:
        """Return the number of runs scored by the batting team."""
        return self.batting_runs

    def __int__(self) -> int:
        """Return the number of runs scored by the batter."""
        return self.runs

    def __post_init__(self) -> None:
        """Initialise field values that depend on one or more other fields."""
        self.bowling_extras = self.no_balls + self.wides
        self.fielding_extras = self.leg_byes + self.byes + self.penalty
        self.extras = self.bowling_extras + self.fielding_extras
        self.bowling_runs = abs(self) - self.fielding_extras
        self.bowling_wickets = sum(1 for wicket in self.dismissals if wicket.mode in BOWLING_WICKET_MODES)
        self.wickets = sum(1 for wicket in self.dismissals if wicket.mode not in cs.KindValues.RETIRED_HURT)

    def __repr__(self) -> str:
        """Return a `repr` string for the ball."""
        return type(self).__name__ + '({}): {}, {} ov'.format(self, self.score, self.index_str)

    def __str__(self) -> str:
        """Return a `str` of the ball's outcome."""
        return self.value


class RealBall(Ball):
    """
    Represents a delivery in an existing cricket match. JSON data is passed
    to update inning and player statistics based on the outcome of the ball.
    
    """

    __slots__ = ['data']

    batter: RealBatter
    non_striker: RealBatter
    bowler: RealBowler
    dismissals: list[RealWicket]

    def __init__(self, data: cs.BallDict, ov: RealOver, inn: RealInning, mat: RealMatch) -> None:
        self.data = data
        abs_index = abs(ov)
        bowler_name = data[cs.DeliveriesKeys.BOWLER]
        batting_runs = data[cs.DeliveriesKeys.RUNS][cs.RunsKeys.TOTAL]
        extras_data = data.get(cs.DeliveriesKeys.EXTRAS, {})
        no_balls = int(cs.ExtrasKeys.NO_BALLS in extras_data)
        wides = extras_data.get(cs.ExtrasKeys.WIDES, 0)
        leg_byes = extras_data.get(cs.ExtrasKeys.LEG_BYES, 0)
        byes = extras_data.get(cs.ExtrasKeys.BYES, 0)
        penalty = extras_data.get(cs.ExtrasKeys.PENALTY, 0)
        dismissals = [RealWicket(wicket_data, bowler_name) for wicket_data in data.get(cs.DeliveriesKeys.WICKETS, [])]

        kwargs = {
            'abs_index': abs_index,
            'index_str': str(ov.index + (abs_index + 1) * 0.1),
            'batter': inn.get_batter(data[cs.DeliveriesKeys.BATTER], mat),
            'non_striker': inn.get_batter(data[cs.DeliveriesKeys.NON_STRIKER], mat),
            'bowler': ov.get_bowler(bowler_name, inn, mat),
            'runs': data[cs.DeliveriesKeys.RUNS][cs.RunsKeys.BATTER],
            'batting_runs': batting_runs,
            'boundary': batting_runs in [4, 6] and cs.RunsKeys.NON_BOUNDARY not in self.data[cs.DeliveriesKeys.RUNS],
            'no_balls': no_balls,
            'wides': wides,
            'leg_byes': leg_byes,
            'byes': byes,
            'penalty': penalty,
            'dismissals': dismissals,
            'value': self._value(batting_runs, no_balls, wides, leg_byes, byes, penalty, dismissals)
        }

        super().__init__(index=len(ov), **kwargs)

    def run(self, ov: RealOver, inn: RealInning, mat: RealMatch) -> None:
        """Update inning and player statistics."""
        # if cs.ReplacementsKeys.ROLE in self.data.get(cs.DeliveriesKeys.REPLACEMENTS, {}):
            # self._add_batting_replacements(inn, mat)
        batter = self.batter
        batter.update(self)

        bowler = self.bowler
        bowler.update(self, ov)

        inn.update_score_and_pship(self)
        self.score = inn.score
        self.pship = inn.pship_str(bool(self.wickets))

        if self.dismissals:
            inn.update_dismissal(self, mat)

        self.batter = deepcopy(batter)
        self.non_striker = deepcopy(self.non_striker)
        self.bowler = ov.bowlers[-1] = deepcopy(bowler)

    def _value(
            self,
            batting_runs: int,
            no_balls: int,
            wides: int,
            leg_byes: int,
            byes: int,
            penalty: int,
            dismissals: list[Wicket]
    ) -> str:
        """Return a string for the ball's outcome."""
        if wides:
            value = '{}wd'.format(wides - 1)
        elif leg_byes:
            value = '{}lb'.format(leg_byes)
        elif byes:
            value = '{}b'.format(byes)
        else:
            value = str(batting_runs)

        if no_balls:
            if leg_byes or byes:
                value += '+'
            value += 'nb'

        if dismissals and dismissals[0].mode not in cs.KindValues.RETIRED_HURT:
            if dismissals[0].mode == cs.KindValues.RUN_OUT:
                value += '+W'
            elif wides:
                value += '/W'
            else:
                value = 'W'

        if penalty:
            value += '{}p'.format(penalty)

        return value



#   def _add_batting_replacements(self, inn: Inning, mat: Match) -> None:  # move to Inning.get_batter
#         """Add a new batter if the current batter is retired hurt."""
#         for replacements_data in self.data[cs.DeliveriesKeys.REPLACEMENTS][cs.ReplacementsKeys.ROLE]:
#             if replacements_data[cs.RoleKeys.ROLE] == cs.RoleValues.BATTER:
#                 new = inn.at_crease.pop()
#                 out = inn.get_batter(replacements_data[cs.RoleKeys.OUT], mat)
#                 out.dismissal = 'retired hurt'
#                 inn.pships.append(inn.pship_str(False))
#                 inn.at_crease.remove(out)
#                 inn.at_crease.append(new)
#                 inn.pship[:] = 0

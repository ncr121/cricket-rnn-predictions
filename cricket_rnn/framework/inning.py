"""
``cricket_rnn.framework.inning``
================================

"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from cricket_rnn.framework import (
    Batter,
    Bowler,
    Fielder,
    List,
    Over,
    RealBall,
    RealBatter,
    RealBowler,
    RealFielder,
    RealOver,
    RealPlayer,
    attrlister
)
import cricket_rnn.loaders.cricinfo as ci
import cricket_rnn.loaders.cricsheet as cs

if TYPE_CHECKING:
    from . import RealMatch


@dataclass(eq=False, kw_only=True, slots=True)
class Inning:
    """
    Base class for any object that represents an inning of a cricket match.
    Computes inning statistics such as scorecards, fall of wickets and
    partnerships from `Ball` instances contained in the `overs` attribute.
    
    """

    index: int
    batting_team: str
    fielding_team: str
    super_over: bool
    overs: list[Over] = field(default_factory=list)
    batters: List[Batter] = field(default_factory=List)
    bowlers: List[Bowler] = field(default_factory=List)
    fielders: List[Fielder] = field(default_factory=List)
    fow: list[str] = field(default_factory=list)
    declared: bool = False
    _pships: list[str] = field(default_factory=list)
    title: str = field(init=False)
    _score: np.ndarray = field(init=False)

    def __getitem__(self, over_id: int) -> Over:
        """Return the n<sup>th</sup> over of the inning."""
        return self.overs[over_id]

    def __len__(self) -> int:
        """Return the number of overs in the inning."""
        return len(self.overs)

    def __post_init__(self) -> None:
        """Initialise field values that depend on one or more other fields."""
        if self.super_over:
            self.title = '{} Super Over'.format(self.batting_team)
        else:
            self.title = '{} {} Innings'.format(self.batting_team, '1st' if self.index < 2 else '2nd')

        try:
            self._score = np.array(self[-1][-1].score.replace('d', '').split('-'), dtype=int)
        except IndexError:
            self._score = np.zeros(2, dtype=int)

    def __repr__(self) -> str:
        """Return a `repr` string for the inning."""
        return type(self).__name__ + '({}): {}'.format(self.index, self.score)

    @property
    def bat_card(self) -> pd.DataFrame:
        """Return the batting scorecard for the inning."""
        stats = attrlister(self.batters, 'long_name', 'dismissal', 'runs', 'balls', 'fours', 'sixes', 'strike_rate')
        card = pd.DataFrame(stats, columns=['Name', '', 'R', 'B', '4s', '6s', 'S/R']).set_index('Name')

        try:
            score = str(self._score[0]) if self._score[1] == 10 else self.score
            index = self[-1].index + abs(self[-1]) * 0.1
            overs = '{} ov'.format(index if abs(self[-1]) % 6 else int(index) + int(abs(self[-1]) == 6))
            run_rate = 'RR: {:.2f}'.format(self._score[0] / (int(index) + index % 1 / 0.6 + 1e-5))
            extras = 'Extras: {}'.format(self._score[0] - sum(card['R']))
            card.loc['Total'] = ['', '', score, overs, run_rate, extras]
        except IndexError:
            print(121)
            card.loc['Total'] = ['', '', '0 - 0', '0 ov', 'RR: 0.00', 'Extras: 0']

        return card

    @property
    def bowl_card(self) -> pd.DataFrame:
        """Return the bowling scorecard for the inning."""
        stats = attrlister(self.bowlers, 'long_name', 'overs', 'maidens', 'runs', 'wickets', 'extras', 'economy')
        card = pd.DataFrame(stats, columns=['Name', 'O', 'M', 'R', 'W', 'Extras', 'Econ']).set_index('Name')
        card.loc['Total'] = list(self.bat_card.iloc[-1])

        return card

        # @property

    @property
    def pships(self) -> list[str]:
        """Return the batting partnerships of the inning."""
        pships = self._pships.copy()
        if not pships or pships[-1] != (pship := self[-1][-1].pship):
            pships.append(pship)
        return pships

    @property
    def score(self) -> str:
        """Return a `str` of the current score of the inning."""
        return '{}-{}{}'.format(*self._score, 'd' if self.declared else '')

    @property
    def scorecard(self) -> pd.DataFrame:
        """Return the ball-by-ball scorecard of the inning."""
        card = pd.DataFrame([[''] * 6] + [str(ov).split() for ov in self]).fillna('').drop(0).rename_axis('Over')
        card.columns += 1
        card.insert(0, 'Bowler', ['/'.join(bowler.long_name for bowler in ov.bowlers) for ov in self])
        card['Score'] = attrlister(self, 'score')

        return card

    def best_scores(self, attr: str, n: int) -> list[str]:
        """Return the `n` best scores of the inning for a specific role."""
        return attrlister(sorted(getattr(self, attr), reverse=True)[:n], 'long_name', 'score')


class RealInning(Inning):
    """
    Represents an inning in an existing cricket match. JSON data is passed to
    the framework ball by ball in order to update inning and player statistics.

    """

    __slots__ = ['data', '_at_crease', '_pship', '_pships']

    overs: list[RealOver]
    batters: List[RealBatter]
    bowlers: List[RealBowler]
    fielders: List[RealFielder]

    def __init__(self, data: cs.InningDict, mat: RealMatch) -> None:
        self.data = data
        batting_team = data[cs.InningsKeys.TEAM]

        kwargs = {
            'batting_team': batting_team,
            'fielding_team': mat.teams[1 - mat.teams.index(batting_team)],
            'super_over': cs.InningsKeys.SUPER_OVER in data
        }

        super().__init__(index=len(mat), **kwargs)
        self._at_crease: list[RealBatter] = []
        self._pship: np.ndarray = np.zeros((3, 2), dtype=int)
        self._init_fielders(mat)

    def get_batter(self, name: str, mat: RealMatch, *, absent: bool = False) -> RealBatter:
        """Return the main instance for the batter with name `name`. Create a new `Batter` if it doesn't exist."""
        try:
            batter = self.batters[name]
            if batter.dismissal == 'retired hurt':
                batter.dismissal = 'not out'
                self._at_crease.append(batter)
            return batter
        except ValueError:
            return self._new_batter(mat.players[self.batting_team][name], mat, absent)

    def get_bowler(self, name: str, mat: RealMatch) -> RealBowler:
        """Return the main instance for the bowler with name `name`. Create a new `Bowler` if it doesn't exist."""
        try:
            return self.bowlers[name]
        except ValueError:
            return self._new_bowler(mat.players[self.fielding_team][name])

    def get_fielder(self, name: str, mat: RealMatch, substitute: bool = False) -> RealFielder:
        """Return the main instance for the fielder with name `name`. Create a new `Fielder` if it doesn't exist."""
        try:
            return self.fielders[name]
        except ValueError:
            return self._new_fielder(name, mat, substitute)

    def pship_str(self, wicket: bool) -> str:
        """Return a `str` of the current partnership."""
        return '{4}{8} ({5}) ({6} {0} ({1}), {7} {2} ({3}))'.format(*self._pship.flatten(), *self._at_crease, '' if wicket else '*')

    def run(self, mat: RealMatch) -> None:
        """Simulate an inning being played by passing existing outcomes to the framework ball by ball."""
        if cs.PenaltyRunsKeys.PRE in (pre_data := self.data.get(cs.InningsKeys.PENALTY_RUNS, {})):
            self._score[0] += pre_data[cs.PenaltyRunsKeys.PRE]

        for over_data in self.data[cs.InningsKeys.OVERS]:
            self.overs.append(ov := RealOver(over_data, self))
            ov.run(self, mat)

        if cs.InningsKeys.DECLARED in self.data:
            self.declared = True

        if cs.InningsKeys.ABSENT_HURT in self.data:
            for name in self.data[cs.InningsKeys.ABSENT_HURT]:
                self.get_batter(name, mat, absent=True)

        if cs.PenaltyRunsKeys.POST in (post_data := self.data.get(cs.InningsKeys.PENALTY_RUNS, {})):
            self._score[0] += post_data[cs.PenaltyRunsKeys.POST]

    def update_dismissal(self, b: RealBall, mat: RealMatch) -> None:
        """Update after a dismissal."""
        for dismissal in b.dismissals:
            # substitute=self.data[cs.DeliveriesKeys.WICKETS][i].get(cs.FieldersKeys.SUBSTITUTE, False)
            out = self.get_batter(dismissal.batter, mat)
            fielders = [self.get_fielder(name, mat, substitute) for name, substitute in dismissal.fielders.items()]
            out.dismissal = out.set_dismissal(dismissal.mode, b.bowler, fielders)
            for fielder in fielders:
                fielder.update(dismissal.mode)

            self._pships.append(self.pship_str(wicket := dismissal.mode not in cs.KindValues.RETIRED_HURT))
            self._at_crease.remove(out)
            self._pship[:] = 0

            if wicket:
                self.fow.append('{} ({}, {} ov)'.format(b.score, out.long_name, b.index_str))

    def update_score_and_pship(self, b: RealBall) -> None:
        """Update the score and partnership of the inning based on the outcome of the last ball."""
        striker = self._at_crease.index(b.batter)
        self._pship[striker] += [int(b), int(b.wides == 0)]
        self._pship[2] += [abs(b), int(b.wides == 0)]
        self._score += [abs(b), b.wickets]

    def _init_fielders(self, mat: RealMatch) -> None:
        """Instantiate a `Fielder` for every player in the fielding team at the start of the inning."""
        for player in mat.players[self.fielding_team]:
            self.get_fielder(player.name, mat)

    def _new_batter(self, player: RealPlayer, mat: RealMatch, absent: bool = False) -> RealBatter:
        """Instantiate a `Batter` for a new batter in the inning."""
        batter = RealBatter(player, len(self.batters), mat.players[self.batting_team].index(player))
        # player.innings[mat.format][mat.index][ROLES[0]][self.index] = batter
        self.batters.append(batter)

        if absent:
            batter.position = None
            batter.dismissal = 'absent hurt'
        else:
            self._at_crease.append(batter)

        return batter

    def _new_bowler(self, player: RealPlayer) -> RealBowler:
        """Instantiate a `Bowler` for a new bowler in the inning."""
        bowler = RealBowler(player)
        # player.innings[mat.format][mat.index][ROLES[1]][self.index] = bowler
        self.bowlers.append(bowler)

        return bowler

    def _new_fielder(self, name: str, mat: RealMatch, substitute: bool) -> RealFielder:
        """Instantiate a `Fielder` for a new fielder in the inning."""
        try:
            player = mat.players[self.fielding_team][name]
        except ValueError:
            squad = mat.squads[self.fielding_team]
            player = squad.add_player(ci.get_substitute_fielder_info(name, mat.data['other']))

        fielder = RealFielder(player, player == mat.keepers[self.fielding_team], substitute)
        self.fielders.append(fielder)
        # if not substitute:
            # player.innings[mat.format][mat.index][ROLES[2]][self.index] = fielder

        return fielder

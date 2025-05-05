"""
``cricket_rnn.framework.match``
===============================

"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import zip_longest

import pandas as pd

from cricket_rnn.framework import Inning, List, Player, RealInning, RealPlayer, RealSquad, Squad, display_date_range
import cricket_rnn.loaders.cricinfo as ci
import cricket_rnn.loaders.cricsheet as cs


@dataclass(eq=False, kw_only=True, slots=True)
class Match:
    """
    Base class for any object that represents a cricket match.

    """

    index: int
    type: str
    format: str
    venue: str
    dates: str
    event: str
    teams: list[str]
    squads: dict[str, Squad]
    players: dict[str, List[Player]]
    keepers: list[str]
    toss: str
    outcome: str
    innings: list[Inning] = field(default_factory=list)
    description: str = field(init=False)

    @property
    def summary(self) -> pd.DataFrame:
        """Return the standard summary of the match."""
        return self.create_summary()

    def __getitem__(self, inn_id: int) -> Inning:
        """Return the n<sup>th</sup> inning of the match."""
        return self.innings[inn_id]

    def __len__(self) -> int:
        """Return the number of innings in the match."""
        return len(self.innings)

    def __repr__(self) -> str:
        """Return a `repr` string for the match."""
        return type(self).__name__ + '({}-{}): {}'.format(self.format, self.index, self.description)

    def __post_init__(self) -> None:
        """Initialise field values that depend on one or more other fields."""
        self.description = '{}: {} vs {} at {}, {}'.format(self.event, *self.teams, self.venue, self.dates)

    def create_summary(self, window: int = 5) -> pd.DataFrame:
        """Return a summary for the match. The number of rows for each inning summary is specified by `window`."""
        nrows = window - len(self)
        summary = []

        for inn in self:
            total = '{} ({})'.format(*inn.bat_card.iloc[-1, [2, 3]])
            scores = [
                ['{:25}{:>15}'.format(name, score) for name, score in inn.best_scores(attr, nrows)] for attr in ['batters', 'bowlers']
            ]
            summary.extend([('',)*2, (inn.title, '{:>40}'.format(total)), *zip_longest(*scores, fillvalue='')])

        return pd.DataFrame(summary, columns=['{} vs {}'.format(*self.teams), self.dates]).rename_axis(' ')


class RealMatch(Match):
    """
    Represents an existing cricket match. Inning data is passed to the
    framework ball by ball in order to update inning and player statistics.

    """

    __slots__ = ['data']

    squads: dict[str, RealSquad]
    players: dict[str, List[RealPlayer]]
    innings: list[RealInning]

    def __init__(self, mat_id: int) -> None:
        self.data = cs.load_match_data(mat_id)
        self.data['other'] = ci.load_match_data(mat_id)
        info = self.data[cs.JSONKeys.INFO]
        players_info = ci.get_players_info(self.data['other'])
        teams = info[cs.InfoKeys.TEAMS]
        squads = {team: RealSquad(team) for team in teams}

        kwargs = {
            'type': info[cs.InfoKeys.TEAM_TYPE],
            'format':info[cs.InfoKeys.MATCH_TYPE],
            'venue': info[cs.InfoKeys.VENUE],
            'dates': display_date_range(info[cs.InfoKeys.DATES]),
            'event': self._event(info.get(cs.InfoKeys.EVENT, {})),
            'teams': teams,
            'squads': squads,
            'players': self._players(squads, info[cs.InfoKeys.PLAYERS], players_info),
            'keepers': ci.get_keeper_names(players_info),
            'toss': self._toss(info[cs.InfoKeys.TOSS]),
            'outcome': self._outcome(info[cs.InfoKeys.OUTCOME])
        }

        super().__init__(index=mat_id, **kwargs)

    def run(self) -> None:
        """Simulate a match being played by passing existing outcomes to the framework ball by ball."""
        for inning_data in self.data[cs.JSONKeys.INNINGS]:
            self.innings.append(inn := RealInning(inning_data, self))
            inn.run(self)

    def _event(self, event_data: cs.EventDict) -> str:
        """Return a string format of the event the match is a part of."""
        if cs.EventKeys.NAME in event_data:
            event = event_data[cs.EventKeys.NAME]
            if cs.EventKeys.SUB_NAME in event_data:
                event += ', {}'.format(event_data[cs.EventKeys.SUB_NAME])
            if cs.EventKeys.STAGE in event_data:
                event += ' {}'.format(event_data[cs.EventKeys.STAGE])
            if cs.EventKeys.GROUP in event_data:
                event += ' Group {}'.format(event_data[cs.EventKeys.GROUP])
            if cs.EventKeys.MATCH_NUMBER in event_data:
                event += ' Match {}'.format(event_data[cs.EventKeys.MATCH_NUMBER])
            return event
        return ''

    def _outcome(self, outcome_data: cs.OutcomeDict) -> str:
        """Return a string format of the outcome of the match."""
        return outcome_data

    def _players(
        self,
        squads: dict[str, RealSquad],
        players_data: cs.PlayersDict,
        players_info: dict[str, ci.PlayerDict]
    ) -> dict[str, List[RealPlayer]]:
        """Return the players involved in the match for each team."""
        return {team: squad.playing(players_data[team], players_info[team]) for team, squad in squads.items()}

    def _toss(self, toss_data: cs.TossDict) -> str:
        """Return a string format of the toss."""
        return '{} won the toss and chose to {}'.format(toss_data[cs.TossKeys.WINNER], toss_data[cs.TossKeys.DECISION])


def run_match(mat_id: int) -> RealMatch:
    """Generate statistics for match ID `mat_id`."""
    mat = RealMatch(mat_id)
    mat.run()
    return mat

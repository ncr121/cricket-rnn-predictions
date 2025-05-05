"""
``cricket_rnn.framework.squads``
================================

"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Iterator

from cricket_rnn.framework import List
import cricket_rnn.loaders.cricinfo as ci


class Person(ABC):
    """
    Abstract class that represents a person.
    
    """

    name: str
    long_name: str
    short_name: str

    def __eq__(self, other: str | Person) -> bool:
        """Return `True` if another player has the same name."""
        return self.name == getattr(other, 'name', other)

    def __hash__(self) -> int:
        """Return a `hash` for the player."""
        return hash(self.name)

    def __repr__(self) -> str:
        """Return a `repr` string for the player."""
        return type(self).__name__ + '({})'.format(self.long_name)

    def __str__(self) -> str:
        """Return a `str` of the player's name."""
        return self.short_name


@dataclass(repr=False, eq=False, kw_only=True, slots=True)
class Player(Person):
    """
    A cricket player with detailed batting, bowling and fielding statistics
    across all formats.
    
    """

    name: str
    long_name: str
    short_name: str
    id: int
    batting_style: str | None
    bowling_style: str | None
    team: str


class RealPlayer(Player):
    """
    Represents an existing cricket player with their actual styles of play.

    """

    __slots__ = ['data']

    def __init__(self, player_info: ci.PlayerDict, team: str) -> None:
        self.data = player_info

        kwargs = {
            'name': player_info[ci.PlayerKeys.CARD_LONG],
            'long_name': player_info[ci.PlayerKeys.NAME],
            'short_name': player_info[ci.PlayerKeys.MOBILE_NAME],
            'id': player_info[ci.PlayerKeys.ID],
            'batting_style': player_info[ci.PlayerKeys.BATTING_STYLE],
            'bowling_style': player_info[ci.PlayerKeys.BOWLING_STYLE],
        }

        super().__init__(team=team, **kwargs)


@dataclass(eq=False, slots=True)
class Squad:
    """
    A squad of a cricket team.
    
    """

    team: str
    players: dict[str, Player] = field(default_factory=dict)

    def __getitem__(self, name: str) -> Player:
        """Return the player with name `name`."""
        return next(player for player in self if player == name)

    def __iter__(self) -> Iterator:
        """Return an iterator of the players in the squad."""
        return iter(self.players.values())

    def __len__(self) -> int:
        """Return the number of players in the squad."""
        return len(self.players)

    def __repr__(self) -> str:
        """Return a `repr` string for the squad."""
        return type(self).__name__ + '({})'.format(self)

    def __str__(self) -> str:
        """Return the team name."""
        return self.team


class RealSquad(Squad):
    """
    Represents an actual cricket squad.

    """

    players: dict[str, RealPlayer]

    def __init__(self, team: str) -> None:
        super().__init__(team)

    def add_player(self, player_info: ci.PlayerDict) -> Player:
        """Add a new player to the squad."""
        player = RealPlayer(player_info, self.team)
        self.players[player.long_name] = player
        return player

    def playing(self, names: list[str], players_info: dict[str, ci.PlayerDict]) -> List[Player]:
        """Return the playing eleven of a match and add any new players to the squad."""
        for name in names:
            if name not in self:
                self.add_player(players_info[name])

        return List(self[name] for name in names)

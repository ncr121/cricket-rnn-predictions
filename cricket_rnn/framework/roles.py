"""
``cricket_rnn.framework.roles``
===============================
Store and update batting, bowling and fielding statistics for a player during an inning of a cricket match.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from cricket_rnn.framework import Person, RealPlayer
import cricket_rnn.loaders.cricsheet as cs

if TYPE_CHECKING:
    from . import RealBall, RealOver


class Role(Person, ABC):
    """
    Abstract class that represents an inning of a batter or bowler.
    
    """

    name: str
    long_name: str
    short_name: str
    style: str
    balls: str

    @property
    @abstractmethod
    def score(self) -> str:
        """Return a `str` of the player's score."""

    def __add__(self, other: Role) -> Role:
        """Add statistics of two innings."""
        static_attrs = ['name', 'long_name', 'short_name', 'style']
        static_kwargs = {attr: value for attr, value in vars(self) if attr in static_attrs}
        dynamic_kwargs = {attr: value + getattr(other, attr) for attr, value in vars(self) if attr not in static_attrs}

        return self.__class__(**static_kwargs, **dynamic_kwargs)

    def __floordiv__(self, value: int) -> int:
        """Return a metric showing how far the player is into their inning."""
        return (self.balls - 1) // value

    def __lt__(self, other: Role) -> bool:
        """Return `True` if another instance has a better score."""
        if self.balls and other.balls:
            return self._score() < other._score()
        return self.balls < other.balls

    def __repr__(self) -> str:
        """Return a `repr` string for the player."""
        return super().__repr__() + ': {}'.format(self.score)

    @abstractmethod
    def _score(self) -> tuple[int, int, int]:
        """Return a `tuple` of the player's score."""


@dataclass(repr=False, eq=False, slots=True)
class Batter(Role):
    """
    An inning of a batter.
    
    """

    name: str
    long_name: str
    short_name: str
    style: str
    position: int
    true_position: int
    runs: int = 0
    balls: int = 0
    fours: int = 0
    sixes: int = 0
    dismissal: str = 'not out'

    @property
    def out(self) -> bool:
        """Return `True` if the batter is out."""
        return self.dismissal != 'not out'

    @property
    def score(self) -> str:
        """Return a `str` of the batter's score."""
        return '{}{} ({})'.format(self.runs, '' if self.out else '*', self.balls)

    @property
    def strike_rate(self) -> str:
        """Return a `str` of the batter's strike rate."""
        return '{:.2f}'.format(self.runs / (self.balls + 1e-5) * 100)

    def _score(self) -> tuple[int, int, int]:
        """Return a `tuple` of the batter's score."""
        return (self.runs, -self.out, -self.balls)


class RealBatter(Batter):
    """
    Represents an existing inning of a batter.

    """

    def __init__(self, player: RealPlayer, *positions: int) -> None:
        super().__init__(player.name, player.long_name, player.short_name, player.batting_style, *positions)

    def set_dismissal(self, mode: str, bowler: Bowler, fielders: list[RealFielder]) -> str:  # move
        """Return a string representation of the batter's dismissal."""
        if mode == cs.KindValues.BOWLED:
            return 'b {}'.format(bowler)
        if mode == cs.KindValues.LBW:
            return 'lbw b {}'.format(bowler)
        if mode == cs.KindValues.CAUGHT:
            return 'c {} b {}'.format(fielders[0], bowler)
        if mode == cs.KindValues.CAUGHT_AND_BOWLED:
            return 'c & b {}'.format(bowler)
        if mode == cs.KindValues.STUMPED:
            return 'st {} b {}'.format(fielders[0], bowler)
        if mode == cs.KindValues.RUN_OUT:
            if not fielders:
                return 'run out'
            return 'run out ({})'.format('/'.join(fielders))
        if mode in cs.KindValues.RETIRED_HURT:
            return 'retired hurt'
        if mode == cs.KindValues.HIT_WICKET:
            return 'hit wicket b {}'.format(bowler)
        if mode == cs.KindValues.OBSTRUCTING_THE_FIELD:
            return 'obstructing the field'
        if mode == cs.KindValues.TIMED_OUT:
            return 'timed out'
        if mode == cs.KindValues.HANDLED_THE_BALL:
            return 'handled the ball'
        raise ValueError('unseen mode:', mode)

    def update(self, b: RealBall) -> None:
        """Update batting statistics after a ball has been bowled."""
        self.runs += (r_ := int(b))
        self.balls += int(not b.wides)
        self.fours += int(r_ == 4 and b.boundary)
        self.sixes += int(r_ == 6 and b.boundary)


@dataclass(repr=False, eq=False, slots=True)
class Bowler(Role):
    """
    An inning of a bowler.
    
    """

    name: str
    long_name: str
    short_name: str
    style: str
    balls: int = 0
    maidens: int = 0
    runs: int = 0
    wickets: int = 0
    extras: int = 0
    spells: list[np.ndarray] = field(default_factory=list)

    @property
    def economy(self) -> str:
        """Return a `str` of the bowler's economy."""
        return '{:.2f}'.format(self.runs / (self.balls / 6 + 1e-5))

    @property
    def overs(self) -> float | int:
        """Return the number of overs bowled by the bowler."""
        return self.balls // 6 + (self.balls % 6 / 10 if self.balls % 6 else 0)

    @property
    def score(self) -> str:
        """Return a `str` of the bowler's score."""
        return '{}-{} ({})'.format(self.wickets, self.runs, self.overs)

    def _score(self) -> tuple[int, int, int]:
        """Return a `tuple` of the bowler's score."""
        return (self.wickets, -self.runs, self.overs)


class RealBowler(Bowler):
    """
    Represents an existing inning of a bowler.

    """

    def __init__(self, player: RealPlayer) -> None:
        super().__init__(player.name, player.long_name, player.short_name, player.bowling_style)

    def update(self, b: RealBall, ov: RealOver) -> None:
        """Update bowling statistics after a ball has been bowled."""
        self.balls += (b_ := int(not b.bowling_extras))
        self.maidens += (m_ := int(ov.maiden))
        self.runs += (r_ := b.bowling_runs)
        self.wickets += (w_ := int(b.bowling_wickets))
        self.extras += b.bowling_extras
        self.spells[-1] += [b_/6, m_, r_, w_]


@dataclass(repr=False, eq=False, slots=True)
class Fielder(Person):
    """
    An inning of a fielder.
    
    """

    name: str
    long_name: str
    short_name: str
    keeper: bool
    substitute: bool = False
    catches: int = 0
    stumpings: int = 0
    run_outs: int = 0

    def __str__(self) -> str:
        """Return a `str` of the fielder's name, also indicating if they are a keeper or a substitute fielder."""
        if self.substitute:
            return 'sub ({})'.format(self.short_name)
        return ('†' if self.keeper else '') +  self.short_name


class RealFielder(Fielder):
    """
    Represents an existing inning of a fielder.
    
    """

    def __init__(self, player: RealPlayer, keeper: bool, substitute: bool = False) -> None:
        super().__init__(player.name, player.long_name, player.short_name, keeper=keeper, substitute=substitute)

    def update(self, mode: str) -> None:
        """Update fielding statistics after a wicket has been taken."""
        if mode in [cs.KindValues.CAUGHT, cs.KindValues.CAUGHT_AND_BOWLED]:
            self.catches += 1
        elif mode == cs.KindValues.STUMPED:
            self.stumpings += 1
        elif mode == cs.KindValues.RUN_OUT:
            ...

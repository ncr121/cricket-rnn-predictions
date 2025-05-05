"""
``cricket_rnn.framework.over``
==============================

"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from cricket_rnn.framework import Ball, Bowler, RealBall, RealBowler
import cricket_rnn.loaders.cricsheet as cs

if TYPE_CHECKING:
    from . import RealInning, RealMatch


@dataclass(eq=False, kw_only=True, slots=True)
class Over:
    """
    Base class for any object that represents an over in a cricket match.

    """

    index: str
    bowlers: list[Bowler] = field(default_factory=list)
    balls: list[Ball] = field(default_factory=list)
    start_score: str

    @property
    def maiden(self) -> bool:
        """Return `True` if the over is a maiden."""
        if abs(self) == 6 and len(self.bowlers) == 1:
            return sum(abs(b) - b.bowling_extras for b in self) == 0
        return False

    @property
    def score(self) -> str:
        """Return a `str` of the current score of the inning."""
        return self[-1].score if self else self.start_score

    def __abs__(self) -> int:
        """Return the number of legal balls in the over."""
        return sum(1 for b in self if not b.bowling_extras)

    def __getitem__(self, ball_id: int) -> Ball:
        """Return the n<sup>th</sup> ball of the over."""
        return self.balls[ball_id]

    def __len__(self) -> int:
        """Return the number of balls in the over."""
        return len(self.balls)

    def __repr__(self) -> str:
        """Return a `repr` string for the over."""
        return type(self).__name__ + '({}): {}, over:{}'.format(self, self.score, self.index + 1)

    def __str__(self) -> str:
        """Return a `str` of the outcomes of the balls in the over."""
        return ' '.join(str(b) for b in self)


class RealOver(Over):
    """
    Represents an over in an existing cricket match. Over data is passed to the
    framework ball by ball to update inning and player statistics.

    """

    __slots__ = ['data']

    bowlers: list[RealBowler]
    balls: list[RealBall]

    def __init__(self, data: cs.OverDict, inn: RealInning) -> None:
        self.data = data
        super().__init__(index=len(inn), start_score=inn.score)

    def get_bowler(self, name: str, inn: RealInning, mat: RealMatch) -> RealBowler:
        """Return the current `Bowler` and declare a new spell if applicable."""
        bowler = inn.get_bowler(name, mat)
        if bowler not in self.bowlers:
            if len(self.bowlers) > 0 or len(inn) < 3 or bowler != inn[-3].bowlers[-1]:
                bowler.spells.append(np.zeros(4))
            self.bowlers.append(bowler)
        return bowler

    def run(self, inn: RealInning, mat: RealMatch) -> None:
        """Simulate an over being played by passing existing outcomes to the framework ball by ball."""
        for ball_data in self.data[cs.OversKeys.DELIVERIES]:
            self.balls.append(ball := RealBall(ball_data, self, inn, mat))
            ball.run(self, inn, mat)

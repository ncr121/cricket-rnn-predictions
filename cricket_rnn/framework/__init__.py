"""
``cricket_rnn.framework``
=========================
Core framework that runs ball-by-ball data to generate player and match
statistics.

JSON data is passed to the model one ball at a time, containing information
such as the batter, the bowler, the amount of runs scored and any additional
information if there were extras or wickets. The data is processed and batter,
bowler and fielder statistics are updated.

The framework is separated into modules as listed below.

Modules
-------
- `utils`
- `squads`
- `roles`
- `ball`
- `over`
- `inning`
- `match`
- `serialisation`

"""

from .utils import (
    Float,
    List,
    attrlister,
    display_date_range
)
from .squads import (
    Person,
    Player,
    RealPlayer,
    RealSquad,
    Squad
)
from .roles import (
    Batter,
    Bowler,
    Fielder,
    RealBatter,
    RealBowler,
    RealFielder
)
from .ball import (
    Ball,
    RealBall,
    Wicket
)
from .over import (
    Over,
    RealOver
)
from .inning import (
    Inning,
    RealInning,
)
from .match import (
    Match,
    RealMatch,
    run_match
)
from .serialisation import (
    decode_match,
    encode_match
)

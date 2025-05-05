"""
``cricket_rnn.loaders.cricinfo._aliases_and_constants``
=======================================================
Type aliases, keys and values for JSON data from `Cricinfo
<https://www.espncricinfo.com/>`_.

For an example format, go to `1249875 JSON
<https://www.espncricinfo.com/matches/engine/match/1249875.json>`_.

Unlike the Cricsheet aliases, ``JSONDict`` is not exhaustive and only provides
aliases for the fields being used.

"""

from typing import Any

# ================= #
# JSON type aliases #
# ================= #


type _MatchDict = dict[str, str]
type _SeriesDict = dict[str, int | str | None]
type PlayerDict = dict[str, int | str | None]
type _TeamDict = dict[str, int | str | list[PlayerDict]]
type JSONDict = dict[str,
    str |
    _MatchDict |
    list[_SeriesDict] |
    list[PlayerDict] |
    list[_TeamDict] |
    Any
]

# ==================== #
# JSON keys and values #
# ==================== #


class JSONKeys:
    """Keys for the JSON data format."""
    MATCH = 'match'
    SERIES = 'series'
    SUBSTITUTE = 'substitute'
    TEAM = 'team'


class MatchKeys:
    """Keys for the `match` field."""


class SeriesKeys:
    """Keys for the `series` field."""


class TeamKeys:
    """Keys for the `team` field."""
    NAME = 'team_name'
    PLAYER = 'player'


class PlayerKeys:
    """Keys for the `player` field of the `team` field."""
    ID = 'object_id'
    NAME = 'known_as'
    CARD_LONG = 'card_long'
    CARD_SHORT = 'card_short'
    MOBILE_NAME = 'mobile_name'
    BATTING_STYLE = 'batting_style'
    BATTING_STYLE_LONG = 'batting_style_long'
    BOWLING_PACESPIN = 'bowling_pacespin'
    BOWLING_STYLE = 'bowling_style'
    BOWLING_STYLE_LONG = 'bowling_style_long'
    ROLE = 'player_primary_role'
    CAPTAIN = 'captain'
    KEEPER = 'keeper'

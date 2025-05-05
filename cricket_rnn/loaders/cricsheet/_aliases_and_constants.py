"""
``cricket_rnn.loaders.cricsheet._aliases_and_constants``
========================================================
Type aliases, keys and values for JSON data from `Cricsheet
<https://cricsheet.org>`_.

For more information, go to `Introduction to the JSON format
<https://cricsheet.org/format/json/#introduction-to-the-json-format>`_.

"""

# ================= #
# JSON type aliases #
# ================= #

type _MetaDict = dict[str, int | str]
type _BowlOutDict = dict[str, str]
type EventDict = dict[str, int | str]
type _OfficialsDict = dict[str, list[str]]
type OutcomeDict = dict[str, str | dict[str, str]]
type PlayersDict = dict[str, list[str]]
type _RegistryDict = dict[str, dict[str, str]]
type _SupersubsDict = dict[str, str]
type TossDict = dict[str, str | bool]
type InfoDict = dict[str,
    str |
    int |
    list[str] |
    list[_BowlOutDict] |
    EventDict |
    _OfficialsDict |
    OutcomeDict |
    PlayersDict |
    _RegistryDict |
    _SupersubsDict |
    TossDict
]
type _ExtrasDict = dict[str, int]
type _ReplacementsDict = dict[str, list[dict[str, str]]]
type _ReviewDict = dict[str, str | bool]
type _RunsDict = dict[str, int | bool]
type WicketsDict = dict[str, str | list[dict[str, str | bool]]]
type BallDict = dict[str, str | _ExtrasDict | _ReplacementsDict | _ReviewDict | _RunsDict | list[WicketsDict]]
type OverDict = dict[str, str | BallDict]
type _PenaltyDict = dict[str, str]
type _PowerplaysDict = dict[str, float | str]
type _MiscountedOversDict = dict[str, dict[str, str]]
type _TargetDict = dict[str, int]
type InningDict = dict[str,
    str |
    bool |
    list[str] |
    OverDict |
    _PenaltyDict |
    list[_PowerplaysDict] |
    _MiscountedOversDict |
    _TargetDict
]
type JSONDict = dict[str, _MetaDict | InfoDict | InningDict]

# ==================== #
# JSON keys and values #
# ==================== #


class JSONKeys:
    """Keys for the sections in the JSON data format."""
    META = 'meta'
    INFO = 'info'
    INNINGS = 'innings'


class MetaKeys:
    """Keys for the `meta` section."""
    DATA_VERSION = 'data_version'
    CREATED = 'created'
    REVISION = 'revision'


class InfoKeys:
    """Keys for the `info` section."""
    BALLS_PER_OVER = 'balls_per_over'
    BOWL_OUT = 'bowl_out'
    CITY = 'city'
    DATES = 'dates'
    EVENT = 'event'
    GENDER = 'gender'
    MATCH_TYPE = 'match_type'
    MATCH_TYPE_NUMBER = 'match_type_number'
    MISSING = 'missing'
    OFFICIALS = 'officials'
    OUTCOME = 'outcome'
    OVERS = 'overs'
    PLAYER_OF_MATCH = 'player_of_match'
    PLAYERS = 'players'
    REGISTRY = 'registry'
    SEASON = 'season'
    SUPERSUBS = 'supersubs'
    TEAM_TYPE = 'team_type'
    TEAMS = 'teams'
    TOSS = 'toss'
    VENUE = 'venue'


class BowlOutKeys:
    """Keys for the `bowl_out` field in the `info` section."""
    BOWLER = 'bowler'
    OUTCOME = 'outcome'


class EventKeys:
    """Keys for the `event` field in the `info` section."""
    NAME = 'name'
    MATCH_NUMBER = 'match_number'
    GROUP = 'group'
    STAGE = 'stage'
    SUB_NAME = 'sub_name'


class OfficialsKeys:
    """Keys for the `officials` field in the `info` section."""
    MATCH_REFERESS = 'match_referees'
    RESERVE_UMPIRE = 'reserve_umpires'
    TV_UMPIRES = 'tv_umpires'
    UMPIRES = 'umpires'


class OutcomeKeys:
    """Keys for the `outcome` field in the `info` section."""
    BY = 'by'
    BOWL_OUT = 'bowl_out'
    ELIMINATOR = 'eliminator'
    METHOD = 'method'
    RESULT = 'result'
    WINNER = 'winner'


class ByKeys:
    """Keys for the `by` field in the 'outcome' field."""
    INNINGS = 'innings'
    RUNS = 'runs'
    WICKETS = 'wickets'


class RegistryKeys:
    """Keys for the `registry` field in the `info` section."""
    PEOPLE = 'people'


class TossKeys:
    """Keys for the `toss` field in the `info` section."""
    UNCONTESTED = 'uncontested'
    DECISION = 'decision'
    WINNER = 'winner'


class InningsKeys:
    """Keys for the `innings` section."""
    TEAM = 'team'
    OVERS = 'overs'
    ABSENT_HURT = 'absent_hurt'
    PENALTY_RUNS = 'penalty_runs'
    DECLARED = 'declared'
    FORFEITED = 'forfeited'
    POWERPLAYS = 'powerplays'
    MISCOUNTED_OVERS = 'miscounted_overs'
    TARGET = 'target'
    SUPER_OVER = 'super_over'


class PenaltyRunsKeys:
    """Keys for the `penalty_runs` field in the `innings` section."""
    PRE = 'pre'
    POST = 'post'


class PowerplaysKeys:
    """Keys for the `powerplays` field in the `innings` section."""
    FROM = 'from'
    TO = 'to'
    TYPE = 'type'


class MiscountedOversKeys:
    """Keys for the `miscounted_overs` field in the `innings` section."""
    BALLS = 'balls'
    UMPIRE = 'umpire'


class TargetKeys:
    """Keys for the `target` field in the `innings` section."""
    OVERS = 'overs'
    RUNS = 'runs'


class OversKeys:
    """Keys for the `overs` field in the `innings` section."""
    OVER = 'over'
    DELIVERIES = 'deliveries'


class DeliveriesKeys:
    """Keys for the `deliveries` field in the `overs` field."""
    BATTER = 'batter'
    BOWLER = 'bowler'
    EXTRAS = 'extras'
    NON_STRIKER = 'non_striker'
    REPLACEMENTS = 'replacements'
    REVIEW = 'review'
    RUNS = 'runs'
    WICKETS = 'wickets'


class ExtrasKeys:
    """Keys for the `extras` field in the `deliveries` field."""
    BYES = 'byes'
    LEG_BYES = 'legbyes'
    NO_BALLS = 'noballs'
    PENALTY = 'penalty'
    WIDES = 'wides'


class ReplacementsKeys:
    """Keys for the `replacements` field in the `deliveries` field."""
    MATCH = 'match'
    ROLE = 'role'


class MatchKeys:
    """Keys for the `match` field in the `replacements` field."""
    IN = 'in'
    OUT = 'out'
    REASON = 'reason'
    TEAM = 'team'


class RoleKeys:
    """Keys for the `role` field in the `replacements` field."""
    IN = 'in'
    OUT = 'out'
    REASON = 'reason'
    ROLE = 'role'


class RoleValues:
    """Values for the `role` field in the `replacements` field."""
    BATTER = 'batter'
    BOWLER = 'bowler'


class ReviewKeys:
    """Keys for the `review` field in the `deliveries` field."""
    BATTER = 'batter'
    BY = 'by'
    DECISION = 'decision'
    UMPIRE = 'umpire'
    UMPIRES_CALL = 'umpires_call'


class RunsKeys:
    """Keys for the `runs` field in the `deliveries` field."""
    BATTER = 'batter'
    EXTRAS = 'extras'
    NON_BOUNDARY = 'non_boundary'
    TOTAL = 'total'


class WicketsKeys:
    """Keys for the `wickets` field in the `deliveries` field."""
    FIELDERS = 'fielders'
    KIND = 'kind'
    PLAYER_OUT = 'player_out'


class FieldersKeys:
    """Keys for the `fielders` field in the `wickets` field."""
    NAME = 'name'
    SUBSTITUTE = 'substitute'


class KindValues:
    """Values for the `kind` field in the `wickets` field."""
    BOWLED = 'bowled'
    LBW = 'lbw'
    CAUGHT = 'caught'
    CAUGHT_AND_BOWLED = 'caught and bowled'
    STUMPED = 'stumped'
    RUN_OUT = 'run out'
    RETIRED_HURT = ['retired hurt', 'retired not out']
    HIT_WICKET = 'hit wicket'
    OBSTRUCTING_THE_FIELD = 'obstructing the field'
    TIMED_OUT = 'timed out'
    HANDLED_THE_BALL = 'handled the ball'

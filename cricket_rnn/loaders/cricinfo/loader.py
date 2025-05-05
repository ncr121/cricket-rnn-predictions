"""
``cricket_rnn.loaders.cricinfo.loader``
=======================================
Read and load data from `Cricinfo <https://www.espncricinfo.com/>`_.

"""

from http.client import HTTPResponse
import json
import os
import re
import urllib.request
import zlib

from bs4 import BeautifulSoup, Tag

from cricket_rnn.loaders import load_json_match_data, json_data_path
from cricket_rnn.loaders.cricinfo import JSONDict, JSONKeys, PlayerDict, PlayerKeys, TeamKeys

BASE_URL = 'https://www.espncricinfo.com/'
MATCHES_PATH = 'matches/engine/match/{}'
HTML_PATH = MATCHES_PATH + '.html'
JSON_PATH = MATCHES_PATH + '.json'
HEADERS = 'headers.json'


def load_match_data(mat_id: int) -> JSONDict:
    """Load JSON data for match ID `mat_id` from `Cricinfo <https://www.espncricinfo.com/>`_."""
    subpackage = __package__.rsplit('.', maxsplit=1)[-1]
    file = json_data_path(subpackage, mat_id)

    if not os.path.exists(folder := os.path.dirname(file)):
        os.mkdir(folder)

    if not os.path.exists(file):
        with open(file, 'wb') as f:
            f.write(_read_cricinfo_url(JSON_PATH.format(mat_id)))

    return load_json_match_data(subpackage, mat_id)


def get_players_info(json_data: JSONDict) -> dict[str, PlayerDict]:
    """Return information about the players of both teams for a specific match."""
    return {
       team_info[TeamKeys.NAME]: {
            player_info[PlayerKeys.CARD_LONG]: player_info
            for player_info in team_info[TeamKeys.PLAYER]
        } for team_info in json_data[JSONKeys.TEAM]
    }


def get_substitute_fielder_info(name: str, json_data: JSONDict) -> PlayerDict:
    """Return information about a specific substitute player."""
    return next(info for info in json_data[JSONKeys.SUBSTITUTE] if info[PlayerKeys.CARD_LONG] == name)


def get_keeper_names(players_info: dict[str, PlayerDict]) -> dict[str, str | None]:
    """Return the name of the keeper for each team."""
    return {
        team: next((name for name, player_info in team_info.items() if player_info[PlayerKeys.KEEPER]), None)
        for team, team_info in players_info.items()
    }


def get_end_of_session_scores(mat_id: int) -> list[list[str]] :
    """Return the scores at the end of each session in a test match."""
    soup = _read_match_html(mat_id)
    tag = soup.find_all(_is_match_flow_tag)[0]
    pattern = r'(Lunch|Tea|End Of Day): ([\w ]+) - (\d+)/(\d+)(?: in ([\d.]+) overs)?'

    return [list(matches) for matches in re.findall(pattern, tag.text)]


def _abs_path(file: str) -> str:
    """Return the absolute path of a file in the `loaders.cricinfo` subpackage."""
    return os.path.join(os.path.dirname(__file__), file)


def _load_headers() -> dict[str, str]:
    """Load request headers for `Cricinfo <https://www.espncricinfo.com/>`_."""
    with open(_abs_path(HEADERS)) as f:
        return json.load(f)


def _read_cricinfo_url(path: str) -> bytes:
    """Read data from `Cricinfo <https://www.espncricinfo.com/>`_ and return it as bytes."""
    request = urllib.request.Request(BASE_URL + path, headers=_load_headers())
    response: HTTPResponse
    with urllib.request.urlopen(request) as response:
        return zlib.decompress(response.read(), 16 + zlib.MAX_WBITS)


def _read_match_html(mat_id: int) -> BeautifulSoup:
    """Read parsed HTML data from the `Scorecard` tab for a specific match."""
    return BeautifulSoup(_read_cricinfo_url(HTML_PATH.format(mat_id)), 'html.parser')


def _get_full_match_path(mat_id: int) -> str:
    """Get the complete url of a match including the series and match slugs."""
    soup = _read_match_html(mat_id)
    tag = soup.find_all('script', id='__NEXT_DATA__')[0]
    slugs: dict[str, str] = json.loads(tag.text)['query']

    return 'series/{}-{}/{}-{}/'.format(*slugs.values())


def _is_table_tag(tag: Tag) -> bool:
    """Return `True` if `tag` has a specific class that represents a table."""
    return tag.get('class') == [
        'ds-w-full',
        'ds-bg-fill-content-prime',
        'ds-overflow-hidden',
        'ds-rounded-xl',
        'ds-border',
        'ds-border-line',
        'ds-mb-4'
    ]


def _is_match_flow_tag(tag: Tag) -> bool:
    """Return `True` if `tag` has a specific class and its title is `Match Flow`."""
    return _is_table_tag(tag) and tag.find('span').text == 'Match Flow'


def _get_keeper_names(mat_id: int) -> list[str]:
    """Return the name of the keeper for each team."""
    soup = _read_match_html(mat_id)
    tags = soup.find_all(_is_table_tag)[:2]
    pattern = r'π([\w ]+)π†π'

    return [re.findall(pattern, 'π'.join(tag.get_text('π', strip=True).split('π')))[0] for tag in tags]

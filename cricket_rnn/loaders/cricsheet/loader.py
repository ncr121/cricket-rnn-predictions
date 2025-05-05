"""
``cricket_rnn.loaders.cricsheet.loader``
========================================
Read and load data from `Cricsheet <https://cricsheet.org>`_.

"""

import datetime as dt
import os
from typing import Iterator, Iterable, Type, TypeVar
from zipfile import ZipFile

import requests
import pandas as pd

from cricket_rnn import MATCH_FORMATS, MATCH_TYPES, TEAM_TYPES, TEST_NATIONS
from cricket_rnn.loaders import load_json_match_data
from cricket_rnn.loaders.cricsheet._aliases_and_constants import JSONDict

T = TypeVar('T')

MATCH_TYPES_JSON = {
    'Test': 'tests',
    'ODI': 'odis',
    'T20': 't20s',
    'IPL': 'ipl',
    'Hundred': 'hnd'
}
BASE_URL = 'https://cricsheet.org/'
JSON_PATH = 'downloads/{}_male_json.zip'
CSV_FILES = [
    'names.csv',
    'people.csv'
]
MASTER_README = 'MASTER_README.csv'


class MasterColumns:
    """Column labels of `MASTER_README.csv`."""
    MATCH_ID = 'match id'
    DATE = 'date'
    TEAM_TYPE = 'team type'
    MATCH_TYPE = 'match type'
    TEAMS = ['team 1', 'team 2']
    ALL = [MATCH_ID, DATE, TEAM_TYPE, MATCH_TYPE, *TEAMS]


def load_match_data(mat_id: int) -> JSONDict:
    """Load JSON data for match ID `mat_id` from Cricsheet."""
    subpackage = __package__.rsplit('.', maxsplit=1)[-1]
    return load_json_match_data(subpackage, mat_id)


def download_csvs() -> None:
    """Download `names.csv` and `people.csv` from the `Cricsheet Register <https://cricsheet.org/register>`_."""
    for file in CSV_FILES:
        _download_cricsheet_url('register/' + file, file)


def read_csv(file, col: str, *, dtype: Type[T]) -> dict[str, T]:
    """Read in a CSV file and return it as a dictionary with the `'identifier'` column as keys and `col` column as values."""
    return dict(pd.read_csv(_abs_path(file)).set_index('identifier')[col].dropna().astype(dtype))


def read_names_csv() -> dict[str, str]:
    """Read in `names.csv` as a dictionary."""
    return read_csv(CSV_FILES[0], 'name', dtype=str)


def read_people_csv() -> dict[str, int]:
    """Read in `people.csv` as a dictionary."""
    return read_csv(CSV_FILES[1], 'key_cricinfo', dtype=int)


def download_json_data() -> None:
    """Download ball-by-ball data for all match types and create a master list."""
    for label, mat_type in MATCH_TYPES_JSON.items():
        print('Downloading', label, 'matches')
        path = JSON_PATH.format(mat_type)
        temp_file = _abs_path('temp.zip')
        _download_cricsheet_url(path, temp_file)

        with ZipFile(temp_file, 'r') as z:
            members = z.namelist()
            z.extract(members.pop(members.index('README.txt')), os.path.dirname(__file__))
            z.extractall(_abs_path('matches_json/'), members)
        os.remove(temp_file)

        readme = _get_readme(label)
        if os.path.exists(readme):
            os.remove(readme)
        os.rename(_abs_path('README.txt'), readme)

    _create_master_list()


def read_master_list() -> pd.DataFrame:
    """Read in the master README file."""
    return pd.read_csv(_abs_path(MASTER_README)).set_index(MasterColumns.MATCH_ID)


def filter_master_list(
        team_types: Iterable[str] | None = None,
        mat_types: Iterable[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        teams_superset: Iterable[str] | None = None,
        teams_subset: Iterable[str] | None = None
) -> pd.DataFrame:
    """Filter matches based on team type, match type, date and the teams involved."""
    df = read_master_list()

    if team_types is None:
        team_types = TEAM_TYPES
    if mat_types is None:
        mat_types = MATCH_TYPES
    if start_date is None:
        start_date = '2000-01-01'
    if end_date is None:
        end_date = str(dt.date.today())
    if teams_superset is None:
        teams_superset = set(df[MasterColumns.TEAMS].values.flatten())
    if teams_subset is None:
        teams_subset = teams_superset

    return df[
        (start_date <= df[MasterColumns.DATE]) &
        (end_date >= df[MasterColumns.DATE]) &
        (df[MasterColumns.TEAM_TYPE].isin(team_types)) &
        (df[MasterColumns.MATCH_TYPE].isin(mat_types)) &
        (df[MasterColumns.TEAMS].isin(teams_superset).all(axis=1)) &
        (df[MasterColumns.TEAMS].isin(teams_subset).any(axis=1))
    ]


def filter_international_matches(
        mat_formats: Iterable[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        teams_superset: Iterable[str] | None = None,
        teams_subset: Iterable[str] | None = None
) -> pd.DataFrame:
    """Filter international matches based on match format, date and the teams involved."""
    if mat_formats is None:
        mat_formats = MATCH_FORMATS
    if teams_superset is None:
        teams_superset = TEST_NATIONS

    return filter_master_list(TEAM_TYPES[:1], mat_formats, start_date, end_date, teams_superset, teams_subset)


def _abs_path(file: str) -> str:
    """Return the absolute path of a file in this directory."""
    return os.path.join(os.path.dirname(__file__), file)


def _download_cricsheet_url(path: str, file: str) -> None:
    """Download data from `Cricsheet <https://cricsheet.org>`_ and write it to a file."""
    with open(file, 'wb') as f:
        f.write(requests.get(BASE_URL + path, timeout=5).content)


def _get_readme(label: str) -> str:
    """Return the README filename for a specific match type."""
    return _abs_path('README_{}.txt'.format(label.upper()))


def _get_basic_match_info(readme: str) -> Iterator[tuple[str, str, str, str, str, str]]:
    """Parse a README file and return basic information about each match."""
    with open(readme) as f:
        for line in reversed(f.readlines()):
            try:
                date, mat_type, mat_format, _, mat_id, teams = line.rstrip('\n').split(' - ')
                yield mat_id, date, mat_type, mat_format, *teams.split(' vs ')
            except ValueError:
                break


def _create_master_list() -> None:
    """Create a master CSV file with information for all match types."""
    info = []
    for label in MATCH_TYPES_JSON:
        readme = _get_readme(label)
        info.extend(_get_basic_match_info(readme))
        os.remove(readme)

    df = pd.DataFrame(info, columns=MasterColumns.ALL).sort_values(MasterColumns.DATE, ascending=False)
    df.to_csv(_abs_path(MASTER_README), index=False)

"""
``cricket_rnn.loaders``
=======================
Read JSON data from `Cricsheet <https://cricsheet.org>`_ and `Cricinfo
<https://www.espncricinfo.com/>`_.

Subpackages
-----------
- ``cricsheet``:
    Read JSON and CSV data from `Cricsheet <https://cricsheet.org>`_
- ``cricinfo``:
    Read JSON and HTML data from `Cricinfo <https://www.espncricinfo.com/>`_

"""

import json
import os
from typing import Any


def json_data_path(subpackage: str, mat_id: int) -> str:
    """Return the absolute path for match ID `mat_id` for the directory `subpackage`."""
    return os.path.join(os.path.dirname(__file__), subpackage, 'matches_json', f'{mat_id}.json')


def load_json_match_data(subpackage: str, mat_id: int) -> dict[str, Any]:
    """Load JSON data for match ID `mat_id` for the directory `subpackage`."""
    return json.load(open(json_data_path(subpackage, mat_id), encoding='utf-8'))

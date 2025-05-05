"""
``cricket_rnn.framework.serialisation``
=======================================

"""

import json
from typing import Any

import numpy as np

from cricket_rnn import framework
from cricket_rnn.framework import Match, RealMatch

type JSONObject = str | float | int | list[JSONObject] | dict[str, JSONObject] | None

POST_INIT = {
    'Ball': ['bowling_extras', 'fielding_extras', 'extras', 'bowling_runs', 'bowling_wickets', 'wickets'],
    'Inning': ['title', '_score'],
    'Match': ['description']
}


def serialise_framework(obj: Any) -> JSONObject:
    """Return a serialisable object for `obj` by using the attributes listed in the `__slots__` special attribute."""
    if isinstance(obj, np.ndarray):
        return obj.round(1).tolist()
    try:
        base_cls = type(obj).__base__
        attrs = {attr for attr in base_cls.__slots__ if attr not in POST_INIT.get(base_cls.__name__, [])}
        return {'__class__': base_cls.__name__, **{attr: getattr(obj, attr) for attr in attrs}}
    except AttributeError:
        return json.JSONEncoder().default(obj)


def encode_match(mat: RealMatch) -> str:
    """Serialise `mat` to a JSON formatted `str`."""
    return json.dumps(mat, default=serialise_framework)


def deserialise_framework(d: dict) -> dict | Any:
    """Return a `cricket_rnn.framework` object by passing `d` as kwargs to the class constructor."""
    try:
        return getattr(framework, d.pop('__class__'))(**d)
    except KeyError:
        return d


def decode_match(s: str) -> Match:
    """Deserialise `s` to a `Match` object."""
    return json.loads(s, object_hook=deserialise_framework)

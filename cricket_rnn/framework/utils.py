"""
``cricket_rnn.framework.utils``
===============================
Utility classes and functions for the `cricket_rnn.framework` subpackage.

Classes
-------
- `Float`
- `List`

Functions
---------
- `attrlister`
- `display_date_range`

"""

import datetime as dt
from operator import attrgetter
from typing import Iterable, TypeVar, overload

T = TypeVar('T')


class Float(float):
    """A modified `float` that deals with `ZeroDivisionError`."""
    def __truediv__(self, value: float) -> float:
        """Return `x/y` for non-zero `y`. If `y = 0` return `float('inf')` for non-zero `x` else return `0`."""
        try:
            return super().__truediv__(value)
        except ZeroDivisionError:
            return type(self).__base__('inf' if self else 0)


class List(list[T]):
    """A modified `list` that accepts an element of the list as an index to `__getitem__`."""
    def __getitem__(self, y: int | T) -> T:
        """Return `x[y]` if `y` is an integer. If `y` is in `x` return `x[x.index(y)]` else raise `ValueError`."""
        try:
            return super().__getitem__(y)
        except TypeError:
            return super().__getitem__(super().index(y))


def attrlister(objs: Iterable[T], *attrs: str) -> list:
    """Return `operator.attrgetter(*attrs)` applied to every element in `objs`."""
    return [attrgetter(*attrs)(obj) for obj in objs]


@overload
def display_date(date_string: str, input_format: str, output_format: str) -> str:
    ...


@overload
def display_date(date_string: str, input_format: str, output_format: None = None) -> dt.datetime:
    ...


def display_date(date_string: str, input_format: str, output_format: str | None = None) -> dt.datetime | str:
    """Return `date_string` as a `datetime.datetime` object or as reformatted as a string with a different format."""
    date = dt.datetime.strptime(date_string, input_format)
    if output_format is None:
        return date
    return date.strftime(output_format)


def display_date_range(date_strings: Iterable[str]) -> str:
    """Return a string representation showing the start and end of a range of dates."""
    input_format = r'%Y-%m-%d'
    output_format = r'%b %d %Y'

    if len(date_strings) == 1:
        return display_date(date_strings[0], input_format, output_format)

    start_date, *_, end_date = [display_date(date_string, input_format) for date_string in date_strings]

    if start_date.month == end_date.month:
        output_format_ = r'%b'
        return '{} {}-{} {}'.format(start_date.strftime(output_format_), start_date.day, end_date.day, start_date.year)
    if start_date.year == end_date.year:
        output_format_ = r'%b %d'
        return '{}-{} {}'.format(start_date.strftime(output_format_), end_date.strftime(output_format_), start_date.year)
    return '{}-{}'.format(start_date.strftime(output_format), end_date.strftime(output_format))

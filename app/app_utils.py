# Utility functions to be used by app.py
from dateutil import parser

valid_keys = frozenset(["start", "end"])
empty_set = set()

def validate_filenames(start, end) -> bool:
    try:
        if start != "beginning":
            start = parser.parse(start)
        if end:
            end = parser.parse(end)
        return True
    except ValueError:
        return False

def validate_args(d: dict) -> bool:
    return ((d.keys() - valid_keys) == empty_set) and ("start" in d)

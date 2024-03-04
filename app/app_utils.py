# Utility functions to be used by app.py
from dateutil import parser

def validate_filenames(start, end):
    try:
        start = parser.parse(start)
        if end:
            end = parser.parse(end)
        return True
    except ValueError:
        return False


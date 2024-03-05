# Utility functions to be used by app.py
from dateutil import parser
from datetime import timezone
import json # to convert dict to string in get_contents() function
from typing import List, Tuple
import pyarrow.parquet as pq

import duckdb

valid_keys = frozenset(["start", "end"])
empty_set = set()
PAGESIZE = 100

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


def get_filenames(*, start, end=None) -> List[Tuple[str]]:
    if start == "beginning":
        query = "SELECT * FROM dates"
        if end:
            query += f" WHERE dt_aware < '{end}'"
    else:
        query = f"SELECT * FROM dates WHERE dt_aware >= '{start}'"
        if end:
            query += f" AND dt_aware < '{end}'"
    with duckdb.connect("./2024/02/28/filenames.duckdb") as con:
        result = con.sql(query)
        return result.fetchall()

def get_contents(*, start, end=None):
    tuples = get_filenames(start=start, end=end)
    filenames = [t[0].astimezone(timezone.utc).isoformat() for t in tuples]

    for fname in filenames:
        pq_file = pq.ParquetFile(f"./2024/02/28/{fname}.parquet")
        for i in pq_file.iter_batches(PAGESIZE):
            yield json.dumps(i.to_pydict())
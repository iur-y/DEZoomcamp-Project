#!/usr/bin/env python3

# app_utils.py: utility functions to be used by app.py

from dateutil import parser
from datetime import datetime, timedelta
import json # to convert dict to string in get_contents() function
import pyarrow.parquet as pq
from pyarrow.fs import GcsFileSystem
from google.cloud import storage

valid_keys = frozenset(["start", "end"])
empty_set = set()
PAGESIZE = 200
BUCKET = "api_producer_data_zoomcamp_project"
gcs = GcsFileSystem()

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

def add_1us(start):
    """
    Adds one microsecond to start
    This facilitates calling the API with the start argument
    """
    one_us = timedelta(microseconds=1)
    dt = datetime.fromisoformat(start)
    new_dt = dt + one_us
    return new_dt.isoformat()

def prepend_yyyy_mm_dd(iso_dt):
    # iso format: 
    # 2024-03-26T19:58:21.575796+00:00
    # drop everything that comes after T
    tup = iso_dt.partition("T")

    date = tup[0].split("-")
    year = date[0]
    month = date[1]
    day = date[2]

    return f"{year}/{month}/{day}/{iso_dt}.parquet"

def iso_from_blob(blobname):
    """
    Extract valid iso 8601 datetime string from the full blob name
    in GCS.

    Example of blob name:
        2024/03/26/2024-03-26T21:48:59.492914+00:00.parquet
    Objective:
        2024-03-26T21:48:59.492914+00:00
    """
    fname = blobname.removesuffix(".parquet")

    # split on / and get the last element of the split
    return fname.split("/")[-1]

def list_blobs(bucket_name, start=None, end=None):

    if start == "beginning":
        start_offset = None
    else:
        start_offset = prepend_yyyy_mm_dd(add_1us(start))
    
    if end:
        end_offset = prepend_yyyy_mm_dd(end)
    else:
        end_offset = None

    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name,
                                      start_offset=start_offset,
                                      end_offset=end_offset)

    # Note: The call returns a response only when the iterator is consumed.
    for blob in blobs:
        yield blob.name, iso_from_blob(blob.name)

def get_contents(*, start, end=None):

    for fname, iso_dt in list_blobs(BUCKET, start=start, end=end):

        pq_file = pq.ParquetFile(f"{BUCKET}/{fname}", filesystem=gcs)
        for i in pq_file.iter_batches(PAGESIZE):
            d = i.to_pydict()
            d["Timestamp"] = iso_dt # add timestamp key to help client track
            yield json.dumps(d) + "\n"
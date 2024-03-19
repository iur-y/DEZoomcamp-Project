# consume-api.py: creates files locally with the contents from a call to my API

import asyncio
from datetime import datetime, timezone
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import json
import requests
from typing import Generator

schema = pa.schema([
    ("Name", pa.string()),
    ("Platform", pa.string()),
    ("Genre", pa.string()),
    ("Publisher", pa.string()),
    ("NA_Sales", pa.int64()),
    ("EU_Sales", pa.int64()),
    ("JP_Sales", pa.int64()),
    ("Other_Sales", pa.int64()),
    ("Global_Sales", pa.int64()),
    ("Date", pa.string()),
    ("Refunds", pa.int64())
])

def parse_response(batch: bytes, *, encoding="utf-8") -> dict:
    """
    Decodes bytes into string, and then transforms the string into
    dictionary
    batch: raw byte response from API call
    """
    decoded_batch = batch.decode(encoding)
    return json.loads(decoded_batch)

def make_request(*, url, params, stream=True) -> Generator[bytes, None, None]:
    with requests.get(url, params=params, stream=stream) as response:
        try:
            response.raise_for_status()
        except:
            print("Request failed with status code:", response.status_code)
            print("Contents:\n", response.text, sep='')
        else:
            gen = response.iter_lines()
            for batch in gen:
                if batch:
                    yield batch

async def write_file(df, timestamp):
    print("Writing batch with length", len(df))
    # now = datetime.now(timezone.utc).isoformat()
    # writer = pq.ParquetWriter(f'{now}.parquet', schema=schema)
    writer = pq.ParquetWriter(f'{timestamp}.parquet', schema=schema)
    rb = pa.RecordBatch.from_pandas(df, preserve_index=False, schema=schema)
    writer.write_batch(rb)
    writer.close()
    return timestamp

async def get_batches(*, url, params, stream=True, encoding="utf-8"):
    df = pd.DataFrame()
    counter = dict() # Once this has two keys, the DataFrame gets yielded
    response = make_request(url=url, params=params, stream=stream)
    for batch in response:
        batch = parse_response(batch, encoding=encoding)
        timestamp = batch.pop("Timestamp")
        counter[timestamp] = None # None is a dummy value, the key is what matters

        if len(counter) == 2:
            print("Resetting the dict and yielding df")
            yield df, list(counter)[-1] # yields the last key of the dict
            # After yielding, we create fresh counter and DataFrame
            counter = dict()
            df = pd.DataFrame()

        record_df = pd.DataFrame.from_dict(batch)
        df = pd.concat([df, record_df]) # builds up the DataFrame batch by batch

    # Maybe we finish looping but there was an odd number of timestamps,
    # meaning one last yield is necessary
    if not df.empty:
        print("Yielding df from outside the loop")
        yield df, list(counter)[-1]


async def coordinator(url, params):
    timestamp = None
    async for batch, timestamp in get_batches(url=url, params=params):
        timestamp = await write_file(batch, timestamp)

    # Returns only the last written timestamp to be set as an Airflow variable
    # TODO: For more fault tolerance, ideally the variable is updated
    # each time the writer succeeds in writing a file locally
    return timestamp

if __name__ == "__main__":
    asyncio.run(coordinator(url="http://host.docker.internal:5000/data",
                            params={'start': "beginning"}))

# consume-api.py: creates files locally with the contents from a call to my API

import asyncio
from datetime import datetime, timezone
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import json
import requests

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
    decoded_batch = batch.decode(encoding)
    return json.loads(decoded_batch)

def make_request(*, url, params, stream=True):
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

async def write_file(df):
    print("Writing batch with length", len(df))
    now = datetime.now(timezone.utc).isoformat()
    writer = pq.ParquetWriter(f'{now}.parquet', schema=schema)
    rb = pa.RecordBatch.from_pandas(df, preserve_index=False, schema=schema)
    writer.write_batch(rb)
    writer.close()

async def get_batches(*, url, params, stream=True, encoding="utf-8"):
    df = pd.DataFrame()
    counter = set()
    response = make_request(url=url, params=params, stream=stream)
    for batch in response:
        batch = parse_response(batch, encoding=encoding)
        counter.add(batch.pop("Timestamp"))

        if len(counter) == 2:
            print("Recreating the set and yielding df")
            counter = set()
            yield df
            df = pd.DataFrame()

        record_df = pd.DataFrame.from_dict(batch) # compound dtypes are not implemented in the DataFrame constructor
        df = pd.concat([df, record_df])
    if not df.empty:
        print("Yielding df from outside the loop")
        yield df


async def coordinator():
    async for batch in get_batches(url="http://host.docker.internal:5000/data", params={'start': "beginning"}):
        await write_file(batch)


asyncio.run(coordinator())

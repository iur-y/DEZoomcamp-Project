#!/usr/bin/env python3

# producer.py: creates random videogame records and saves as parquet files in GCS

import pandas as pd
import numpy as np
from random_utils import create_list_of_years, create_num_refunds,\
    create_num_sales, create_random_date, create_random_name
from constants import BASEFILE, NUM_ITERATIONS, sale_columns, dtypes, schema
import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow.fs import GcsFileSystem
from datetime import datetime, timezone

BUCKET = "api_producer_data_zoomcamp_project" + "/"

# Read file into DataFrame
df = pd.read_csv(BASEFILE, dtype=dtypes, header=0)

# Create list of years from 1980 - 2020
years = create_list_of_years()

# Get current time to name the file that is about to be created
dt_obj = datetime.now(timezone.utc)
now = dt_obj.isoformat()

# Extract year, month and day from current time
year = dt_obj.strftime('%Y')
month = dt_obj.strftime('%m')
day = dt_obj.strftime('%d')

# Create writer object that writes directly to GCS bucket
gcs = GcsFileSystem()
writer = pq.ParquetWriter(f"{BUCKET}"
                          f'{year}/{month}/{day}/{now}.parquet',
                          schema=schema, filesystem=gcs)

for _ in range(NUM_ITERATIONS): # around (1 MB, 16000 records) per iteration

    s = df.sample(frac=1.0, replace=True)
    # Modify the value of each sale column such as NA_Sales, EU_Sales, ...
    for column in sale_columns:
        s[column] = s[column].apply(create_num_sales)

    # Global_Sales is the accumulation of all other regions' sales
    s["Global_Sales"] = s.apply(lambda row: row.NA_Sales + row.EU_Sales\
                                + row.JP_Sales + row.Other_Sales, axis=1)

    s["Name"] = s["Name"].apply(create_random_name)
    s["Date"] = np.array([create_random_date(years=years)
                          for _ in range(len(s))])
    s["Refunds"] = s.apply(lambda row:\
                    create_num_refunds(row.Rank, row.Global_Sales), axis=1)
    s.drop("Rank", axis=1, inplace=True)

    # ~ 16k records per RecordBatch means 16k records in a parquet row group,
    # which helps compression, but it's still a small number
    # as the recommended is 1 GB
    rb = pa.RecordBatch.from_pandas(s, preserve_index=False, schema=schema)
    writer.write_batch(rb)

writer.close()

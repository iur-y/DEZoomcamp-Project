import pandas as pd
import numpy as np
from random_utils import create_list_of_years, create_num_refunds,\
    create_num_sales, create_random_date, create_random_name
from constants import BASEFILE, sale_columns, dtypes, schema
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timezone
import duckdb

"""
Next step: decide how app.py is going to read the parquet file and stream the records out
DuckDB?
pq.read_table('example2.parquet').to_pandas()?
"""
# TODO: writer = pq.ParquetWriter('./2024/02/28/24-02-28T18:42:30.parquet', schema) will not create directories, I have to create them, perhaps bash operator?
# TODO: I'll have to check into limiting the resources used by a container so I can have this script and airflow running at the same time
# and I might not want to run both the extraction script and the production script at the same time
# remember that this one is just a script that runs a couple of times while app.py stays up 24/7
# TODO: perhaps generate a new years list once I'm done writing a batch of files
# TODO: parametrize the writer to build the path based on passed year/month/day and then use datetime.now() to generate filename
# TODO: there's this optional ParquetWriter parameter write_statistics=True by default, maybe try to optimize the writer object


# Read file into DataFrame
df = pd.read_csv(BASEFILE, dtype=dtypes, header=0)

# Create list of years from 1980 - 2020
years = create_list_of_years()

# get current time to name the file that is about to be created
dt_obj = datetime.now(timezone.utc)
now = dt_obj.isoformat()

# Create parquet writer, it does not create directories, only filename
""" vvv READ THIS vvv """
# By the way, when I create the directory 2024/03/04 with bash, I have to use UTC time to create them
# and them pass those as parameters to this script so it can enter the correct directory
# app.py will use UTC times to access the directories and read the files as well, so it's important
writer = pq.ParquetWriter(f'./2024/02/28/{now}.parquet', schema)


s = df.sample(frac=1.0, replace=True)
# Modify the value of each sale column such as NA_Sales, EU_Sales, ...
for column in sale_columns:
    s[column] = s[column].apply(create_num_sales)

# Global_Sales is the accumulation of all other regions' sales
s["Global_Sales"] = s.apply(lambda row: row.NA_Sales + row.EU_Sales + row.JP_Sales + row.Other_Sales, axis=1)

s["Name"] = s["Name"].apply(create_random_name)
s["Date"] = np.array([create_random_date(years=years) for _ in range(len(s))])
s["Refunds"] = s.apply(lambda row: create_num_refunds(row.Rank, row.Global_Sales), axis=1)
s.drop("Rank", axis=1, inplace=True)

rb = pa.RecordBatch.from_pandas(s, preserve_index=False, schema=schema)
writer.write_batch(rb)

writer.close()

# add filename entry to duckdb
with duckdb.connect("./2024/02/28/filenames.duckdb") as con:
    con.sql("CREATE TABLE IF NOT EXISTS dates (dt_aware TIMESTAMPTZ)")
    stmt = f"INSERT INTO dates VALUES ('{now}')"
    con.sql(stmt)
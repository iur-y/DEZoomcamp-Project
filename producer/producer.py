import pandas as pd
import random
from random_utils import create_list_of_years, create_num_refunds, create_num_sales, create_random_date, create_random_name
from constants import FILENAME, dtypes, schema
import pyarrow as pa
import pyarrow.parquet as pq

"""
Next step: decide how app.py is going to read the parquet file and stream the records out
DuckDB?
pq.read_table('example2.parquet').to_pandas()?
"""
# TODO: I'll have to check into limiting the resources used by a container so I can have this script and airflow running at the same time
# and I might not want to run both the extraction script and the production script at the same time
# remember that this one is just a script that runs a couple of times while app.py stays up
# TODO: perhaps generate a new years list once I'm done writing a batch of files
# TODO: parametrize the writer to build the path based on passed year/month/day and then use datetime.now() to generate filename

# Read file into DataFrame
df = pd.read_csv(FILENAME, dtype=dtypes, header=0)

# Create list of years from 1980 - 2020
years = create_list_of_years()

# Create parquet writer
writer = pq.ParquetWriter('./2024/02/28/24-02-28T18:42:30.parquet', schema)
for _ in range(10_000):
    # Select random record to make fake data from
    s = df.iloc[[random.randint(0, df.shape[0]-1)]].copy()

    global_sales = 0

    temp = create_num_sales(s["NA_Sales"].values[0])
    global_sales += temp
    s["NA_Sales"] = temp

    temp = create_num_sales(s["EU_Sales"].values[0])
    global_sales += temp
    s["EU_Sales"] = temp

    temp = create_num_sales(s["JP_Sales"].values[0])
    global_sales += temp
    s["JP_Sales"] = temp

    temp = create_num_sales(s["Other_Sales"].values[0])
    global_sales += temp
    s["Other_Sales"] = temp

    s["Global_Sales"] = global_sales

    s["Name"] = create_random_name(s["Name"].values[0])
    s["Date"] = create_random_date(years=years)
    s["Refunds"] = create_num_refunds(s["Rank"].values[0], s["Global_Sales"].values[0])
    s.drop("Rank", axis=1, inplace=True)

    rb = pa.RecordBatch.from_pandas(s, preserve_index=False, schema=schema)
    writer.write_batch(rb)
    # TODO: USE DUCKDB TO READ THE PARQUET WRITTEN FILES

writer.close()

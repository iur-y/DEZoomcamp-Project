import pandas as pd
import random
from random_utils import create_list_of_years, create_num_refunds, create_num_sales, create_random_datetime, create_random_name
from constants import FILENAME, dtypes

# TODO: perhaps generate a new years list once I'm done writing a batch of files

# Read file into DataFrame
df = pd.read_csv(FILENAME, dtype=dtypes, header=0)

# Select random record to make fake data from
s = df.iloc[[random.randint(0, df.shape[0]-1)]].copy()

# Create list of years from 1980 - 2020
years = create_list_of_years()

s["Date"] = create_random_datetime(years=years)
s["Name"] = create_random_name(s["Name"].values[0])
s["NA_Sales"] = create_num_sales(s["NA_Sales"].values[0])
s["EU_Sales"] = create_num_sales(s["EU_Sales"].values[0])
s["JP_Sales"] = create_num_sales(s["JP_Sales"].values[0])
s["Other_Sales"] = create_num_sales(s["Other_Sales"].values[0])

print(repr(s))
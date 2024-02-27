import pandas as pd
import random
from random_utils import create_list_of_years, create_num_refunds, create_num_sales, create_random_date, create_random_name
from constants import FILENAME, dtypes

# TODO: perhaps generate a new years list once I'm done writing a batch of files

# Read file into DataFrame
df = pd.read_csv(FILENAME, dtype=dtypes, header=0)

# Create list of years from 1980 - 2020
years = create_list_of_years()

for _ in range(1):
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

print(repr(s))
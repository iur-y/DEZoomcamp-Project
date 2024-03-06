#!/usr/bin/env python3

import pyarrow as pa

##### Constants for random_utils.py #####
VOWELS_SET = frozenset(["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"])

L_VOWELS = ["a", "e", "i", "o", "u"]
U_VOWELS = ["A", "E", "I", "O", "U"]

L_CONSONANTS = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p",
                "q", "r", "s", "t", "v", "w", "x", "y", "z"]

U_CONSONANTS = ["B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "P",
                "Q", "R", "S", "T", "V", "W", "X", "Y", "Z"]


##### Constants for producer.py #####
BASEFILE = "./base_data/no_year_vgsales.csv"

NUM_ITERATIONS = 10

sale_columns = ("NA_Sales","EU_Sales" ,"JP_Sales" ,"Other_Sales")

# Types for reading the base file
dtypes = {
    "NA_Sales": int,
    "EU_Sales": int,
    "JP_Sales": int,
    "Other_Sales": int,
    "Global_Sales": int,
}

# Schema for converting pandas DataFrame to pyarrow Table
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

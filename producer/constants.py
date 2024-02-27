# Constants for random_utils.py

VOWELS_SET = frozenset(["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"])

L_VOWELS = ["a", "e", "i", "o", "u"]
U_VOWELS = ["A", "E", "I", "O", "U"]

L_CONSONANTS = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p",
                "q", "r", "s", "t", "v", "w", "x", "y", "z"]

U_CONSONANTS = ["B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "P",
                "Q", "R", "S", "T", "V", "W", "X", "Y", "Z"]



# Constants for producer.py

FILENAME = "./base_data/no_year_vgsales.csv"

dtypes = {
    "NA_Sales": int,
    "EU_Sales": int,
    "JP_Sales": int,
    "Other_Sales": int,
    "Global_Sales": int,
}
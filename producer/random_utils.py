import numpy as np
import random
from typing import List
import datetime

VOWELS_SET = frozenset(["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"])

L_VOWELS = ["a", "e", "i", "o", "u"]
U_VOWELS = ["A", "E", "I", "O", "U"]

L_CONSONANTS = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"]
U_CONSONANTS = ["B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "X", "Y", "Z"]

vowels_d = {True: U_VOWELS, False: L_VOWELS}
consonants_d = {True: U_CONSONANTS, False: L_CONSONANTS}

def create_list_of_years(*,
                         mean: int = 2020,
                         std: int = 15,
                         size: int = 5000) -> List[int]:
    """
    This is used by `create_random_datetime`
    Creates a list of years from ~ 1980 to 2020 following a
    normal distribution with mean 2020 and standard deviation 20.
    The list is then filtered so only years below the mean are kept

    size: Number of values to be generated before filtering out.
          Only around half of the size is returned
    """
    # Generate random values following a normal distribution
    normal_values = np.random.normal(loc=mean, scale=std, size=size)

    # Filter out values in the right half
    return [int(value) for value in normal_values if value <= mean and value >= 1980]

def create_random_datetime(*, random_years: List) -> datetime.date:
    """
    Picks an year from random_years (created by `create_list_of_years`)
    and then tries to return a date out of it
    """
    year = random.choice(random_years)
    month = random.randint(1, 12)
    while True:
        try:
            day = random.randint(1, 31)
            date = datetime.date(year, month, day)
            break
        # If the day doesn't exist for that month, try again
        except ValueError:
            pass
    return date

def create_random_name(name: str):
    """
    Picks one to three characters at random and replaces them with
    other random characters. Uppercase characters are replaced with
    uppercase characters. The same applies to lowercase characters.
    Vowels are replaced with vowels and consonants with consonants.

    Notes:
        - there are names with a single character
        - which means there are names with two characters
        - some names contain non-alphanumeric characters such as `+`
    """
    # Define an upper bound so that random.randint can work properly
    length = len(name)
    upper_bound = 3 if length >= 3 else length

    name = list(name)

    # Sample the characters that will be replaced
    # TODO: HANDLE NUMBERS IN THE NAMES
    
    chars_indices = random.sample(range(length), random.randint(1, upper_bound))
    chars_indices = [idx for idx in chars_indices if name[idx] != ' ']  # discard spaces
    chars = [name[idx] for idx in chars_indices]

    # Check which characters are uppercased
    uppers = [char.isupper() for char in chars]

    # Check which are vowels
    vowels = [char in VOWELS_SET for char in chars]

    idx_up_vow = zip(chars_indices, uppers, vowels)

    for idx, upper, vowel in idx_up_vow:
        if vowel:
            name[idx] = vowels_d[upper][random.randint(0, 4)]
        else:
            name[idx] = consonants_d[upper][random.randint(0, 20)]
    
    return ''.join(name)

def create_num_refunds(rank: int, sales: int) -> int:
    """
    Takes the rank of a game and how many global sales the game had
    and returns a random number representing refunds 
    """
    return random.gauss(sales, sales*random.uniform(0.0, 0.25)) * (9.17e-7 * rank + 0.00005)
"""Day 1 challenge"""


# Built-in
from itertools import combinations

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
values = [int(v) for v in read_input("day_01.txt")]
for a, b, c in combinations(values, 3):
    if (a + b + c) == 2020:
        print(a * b * c)
        break

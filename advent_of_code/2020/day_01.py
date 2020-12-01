"""Day 1 challenge"""


# Built-in
from itertools import combinations

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
values = read_input("day_01.txt")
values = [int(v) for v in values]
for a, b, c in combinations(values, 3):
    if (a + b + c) == 2020:
        print(a * b * c)
        break

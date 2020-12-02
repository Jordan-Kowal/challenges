"""Day 1 challenge"""

# Built-in
from itertools import combinations

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
values = [int(v) for v in read_input("day_01.txt")]

# First problem
for a, b in combinations(values, 2):
    if (a + b) == 2020:
        print(a * b)
        break

# Second problem
for a, b, c in combinations(values, 3):
    if (a + b + c) == 2020:
        print(a * b * c)
        break

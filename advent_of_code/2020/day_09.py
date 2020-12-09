"""Day 9 challenge"""


# Built-in
from itertools import combinations

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
NUMBERS = [int(value) for value in read_input("day_09.txt")]
RANGE = 25

# Problem 1
i = RANGE
while True:
    current_number = NUMBERS[i]
    available_numbers = NUMBERS[i - RANGE : i]
    possible_outputs = {a + b for a, b in combinations(available_numbers, 2)}
    if current_number not in possible_outputs:
        break
    i += 1
invalid_number = current_number
print(invalid_number)

# Problem 2
length = 2
result = None
while result is None:
    for i in range(len(NUMBERS) - length):
        numbers = NUMBERS[i : i + length]
        if sum(numbers) == invalid_number:
            result = sum([min(numbers), max(numbers)])
    length += 1
print(result)

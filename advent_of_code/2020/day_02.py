"""Day 2 challenge"""

# Built-in
import re

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
REGEX = r"^(\d+)-(\d+) ([a-z]): (.+)$"


def parse_line(input_line):
    """
    Parses the input line to extract its information
    :param str input_line: Line from the input file
    :return: The first number, second number, enforced letter, and the password
    :rtype: (int, int, str, str)
    """
    match = re.match(REGEX, input_line)
    return (
        int(match.group(1)),
        int(match.group(2)),
        match.group(3),
        match.group(4),
    )


first_total, second_total = 0, 0
for line in read_input("day_02.txt"):
    min_, max_, letter, text = parse_line(line)
    # First problem
    letter_count = text.count(letter)
    if min_ <= letter_count <= max_:
        first_total += 1
    # Second problem
    first = text[min_ - 1]
    second = text[max_ - 1]
    if (first == letter or second == letter) and first != second:
        second_total += 1
print(first_total, second_total)

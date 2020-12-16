"""Day 16 challenge"""

# Built-in
import re
from time import perf_counter

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
RULE_REGEX = r"^(.+): (\d+)-(\d+) or (\d+)-(\d+)$"
TITLE_REGEX = r".+ticket.+"


class Form:
    def __init__(self):
        """Form with rules for each field"""
        self.rules = {}

    def add_rule(self, line):
        """
        Adds a new field and its rules (min/max) to the form from the input file
        :param str line: The input line to parse to understand to rule
        """
        name, first_min, first_max, second_min, second_max = self.parse_rule(line)
        self.rules[name] = (first_min, first_max, second_min, second_max)

    @staticmethod
    def parse_rule(line):
        """
        Parses a input line to extract the fieldname and the min/max values (twice)
        :param str line: Line to parse
        :return: The name, and min/max values for both ranges
        :rtype: str, int, int, int int
        """
        match = re.match(RULE_REGEX, line)
        name = match.group(1)
        first_min = int(match.group(2))
        first_max = int(match.group(3))
        second_min = int(match.group(4))
        second_max = int(match.group(5))
        return name, first_min, first_max, second_min, second_max


class Ticket:
    def __init__(self, form, values):
        """
        Ticket with values but no corresponding fields
        :param Form form: The form it will be associated with
        :param [int] values: All the values on the ticket
        """
        self.form = form
        self.values = values
        self.completely_invalid_values = []
        self.check_completely_invalid_values()

    def check_completely_invalid_values(self):
        """Check if the ticket has value that match 0 form rules"""
        for value in self.values:
            for name, ranges in self.form.rules.items():
                min_1, max_1, min_2, max_2 = ranges
                if min_1 <= value <= max_1 or min_2 <= value <= max_2:
                    break
            else:
                self.completely_invalid_values.append(value)

    @property
    def is_completely_invalid(self):
        """
        :return: Whether the ticket cannot be valid, regardless of the field order
        :rtype: bool
        """
        return len(self.completely_invalid_values) > 0


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
# Setup
start = perf_counter()
form = Form()
tickets = []
my_ticket = None

# Parsing
section = 0
for line in read_input("day_16.txt"):
    if line == "":
        section += 1
        continue
    if section == 0:
        form.add_rule(line)
    else:
        title = re.match(TITLE_REGEX, line)
        if title is None:
            values = [int(value) for value in line.split(",")]
            ticket = Ticket(form, values)
            if section == 1:
                my_ticket = ticket
            tickets.append(ticket)

# ----- Problem 1 -----
invalid_tickets = [t for t in tickets if t.is_completely_invalid]
total = sum(sum(t.completely_invalid_values) for t in invalid_tickets)
print(total)

# ----- Problem 2 -----
# Check which field would work on which index(es)
valid_tickets = [t for t in tickets if not t.is_completely_invalid]
valid_indexes_per_field = []
field_quantity = len(form.rules)
for fieldname, ranges in form.rules.items():
    valid_indexes = set()
    min_1, max_1, min_2, max_2 = ranges
    for i in range(field_quantity):
        for ticket in valid_tickets:
            value = ticket.values[i]
            if not (min_1 <= value <= max_1 or min_2 <= value <= max_2):
                break
        else:
            valid_indexes.add(i)
    valid_indexes_per_field.append((fieldname, valid_indexes))

# We guess which index would work based on the other fields valid indexes
valid_indexes_per_field.sort(key=lambda x: len(x[1]), reverse=True)
field_index_tuples = []
for i in range(len(valid_indexes_per_field) - 1):
    name, current_set = valid_indexes_per_field[i]
    _, next_subset = valid_indexes_per_field[i + 1]
    field_index_tuples.append((name, current_set.difference(next_subset).pop()))

# We compute our response
departure_indexes = [i for f, i in field_index_tuples if f.startswith("departure")]
total = 1
for i in departure_indexes:
    total *= my_ticket.values[i]
print(total)

end = perf_counter()
print(end - start)

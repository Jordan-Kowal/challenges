"""Day 7 challenge"""

# Built-in
import re

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
REGEX_BAG_TYPE = r"^(\w+ \w+) bags contain"
REGEX_BAG_RULES = r"(\d) (\w+ \w+) bag"
MAIN_BAG = "shiny gold"


class Rule:
    def __init__(self, bag, nested_bags):
        self.bag = bag
        self.nested_bags = nested_bags

    @classmethod
    def parse_line(cls, input_line):
        match = re.match(REGEX_BAG_TYPE, input_line)
        bag = match.group(1)
        nested_bags = {
            match.group(2): int(match.group(1))
            for match in re.finditer(REGEX_BAG_RULES, input_line)
        }
        return cls(bag, nested_bags)


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
rules = [Rule.parse_line(line) for line in read_input("day_07.txt")]
rule_dict = {rule.bag: rule for rule in rules}

# Problem 1
valid_outer_bags = set()
bags_to_check = {
    MAIN_BAG,
}
while True:
    valid_bags = set()
    for bag in bags_to_check:
        new_bags_to_check = {
            rule.bag for rule in rules if bag in rule.nested_bags.keys()
        }
        valid_bags.update(new_bags_to_check)
    new_valid_bags = {bag for bag in valid_bags if bag not in valid_outer_bags}
    if len(new_valid_bags) == 0:
        break
    else:
        bags_to_check = new_valid_bags.copy()
        valid_outer_bags.update(bags_to_check)

print(len(valid_outer_bags))

# Problem 2
bags_to_check = [
    (MAIN_BAG, 1),
]
total_count = 0
while True:
    new_bags = []
    for bag, qty in bags_to_check:
        matching_rule = rule_dict[bag]
        bags = [(k, v * qty) for k, v in matching_rule.nested_bags.items()]
        new_bags.extend(bags)
    if len(new_bags) == 0:
        break
    else:
        bags_to_check = new_bags.copy()
        total_count += sum([bag[1] for bag in new_bags])
print(total_count)

"""Day 19 challenge"""


# Built-in
import re
from time import perf_counter

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
RECURSION_LEVEL = 6


def compute_rule_regex(rule_id, problem):
    """
    Recursively build regexes based on the given rules
    Fills the REGEXES dict to avoid computing the same rule several times
    :param str rule_id: ID of the rule we want
    :param int problem: The AOC problem we are doing (1 or 2)
    :return:
    :rtype: str
    """
    # Escape case
    rule = RULES[rule_id]
    if rule in "ab":
        return rule
    # Already done
    if rule_id in REGEXES:
        return REGEXES[rule_id]
    # Special handling of problem 2
    if problem == 2:
        # Repeat rule 42 1 or more times
        if rule_id == "8":
            result = compute_rule_regex("42", 2) + "+"
            REGEXES[rule_id] = result
            return result
        # Can have several 42s followed by the same amount of 31s
        if rule_id == "11":
            r1 = compute_rule_regex("42", problem)
            r2 = compute_rule_regex("31", problem)
            quantities = [
                "{" + str(i) + "}" for i in range(1, RECURSION_LEVEL + 1)
            ]  # DO NOT START AT 0 JFC
            combinaisons = [rf"{r1}{q}{r2}{q}" for q in quantities]
            result = rf"({'|'.join(combinaisons)})"
            REGEXES[rule_id] = result
            return result
    # Recursively build the sub-rules
    groups = rule.split("|")
    result = []
    # Merge using AND
    for group in groups:
        ids = group.strip().split(" ")
        sub_regexes = [compute_rule_regex(id_, problem) for id_ in ids]
        merged_regex = "".join(sub_regexes)
        result.append(merged_regex)
    # Merge using OR
    result = rf"({'|'.join(result)})"
    REGEXES[rule_id] = result
    return result


def split_inputs(content):
    """
    Parses the input file to split the rule and text lines
    :param [str] content: The content of the file
    :return: A list of rules to apply and a list of text to check
    :rtype: [str], [str]
    """
    rule_lines = []
    text_lines = []
    for line in content:
        if line == "":
            continue
        elif re.match(r"^\d", line) is not None:
            rule_lines.append(line)
        else:
            text_lines.append(line)
    return rule_lines, text_lines


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
# Initialization
start = perf_counter()
content = read_input("day_19.txt")
raw_rules, texts = split_inputs(content)

# Builds rules dict
RULES = {}
REGEXES = {}
for input in raw_rules:
    rule_id, rule_text = input.split(": ")
    rule_text = re.sub('"', "", rule_text)
    RULES[rule_id] = rule_text

# Problem 1 or 2
regex = compute_rule_regex("0", 2)
total = 0
for t in texts:
    if re.fullmatch(regex, t) is not None:
        total += 1
print(total)

# Terminate
end = perf_counter()
print(end - start)

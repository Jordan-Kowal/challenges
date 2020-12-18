"""Day 18 challenge"""


# Built-in
from time import perf_counter

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
def find_nested_parentheses(string):
    """
    An equation that could contain nested parentheses
    :param str string: An equation to parse
    :return: A dict with the indexes of opening/closing parentheses per nest level
    :rtype: dict
    """
    indexes = {}
    nested_level = 0
    for i, char in enumerate(string):
        if char == "(":
            nested_level += 1
            current = indexes.get(nested_level, [])
            current.append(i)
            indexes[nested_level] = current
        if char == ")":
            current = indexes.get(nested_level, [])
            current.append(i)
            indexes[nested_level] = current
            nested_level -= 1
    return indexes


def solve_equation(line, solver):
    """
    Solves an equation with nested parentheses
    We find the most nested parentheses, solve the sub-equation, and replace it in the string
    We repeat the process until there are no parentheses left
    :param str line: Line from the input file that represents a math equation
    :return: The result of this equation
    :rtype: int
    """
    string = line
    while True:
        # Identify the most nested groups
        indexes = find_nested_parentheses(string)
        if len(indexes) == 0:
            break
        # Get the indexes for the most nested groups
        higest_nested_level = sorted(list(indexes.keys()))[-1]
        target_indexes = list(zip(*(iter(indexes[higest_nested_level]),) * 2))
        target_indexes.sort(key=lambda x: x[0], reverse=True)
        # Solve these equations and update the string
        for i, j in target_indexes:
            substring = string[i : j + 1]
            value_as_string = str(solver(substring))
            string = string.replace(substring, value_as_string)
    return solver(string)


def solve_substring_left_to_right(text):
    """
    Solve a flat/small equation that has no nested parentheses
    Read from left to right, regardless of the operation
    :param str text: A flat equation to solve
    :return: The result of the given equation
    :rtype: int
    """
    text = text.replace("(", "")
    text = text.replace(")", "")
    inputs = text.split(" ")
    total = 0
    next_operation = total.__radd__
    for input in inputs:
        if input == "+":
            next_operation = total.__radd__
        elif input == "*":
            next_operation = total.__rmul__
        else:
            value = int(input)
            total = next_operation(value)
    return total


def solve_substring_with_precedence(text):
    """
    Same as 'solve_substring' but read the addition first
    :param str text: A flat equation to solve
    :return: The result of the given equation
    :rtype: int
    """
    text = text.replace("(", "")
    text = text.replace(")", "")
    inputs = text.split(" ")

    while len(inputs) > 1:
        if "+" in inputs:
            i = inputs.index("+")
            value = int(inputs[i - 1]) + int(inputs[i + 1])
        else:
            i = inputs.index("*")
            value = int(inputs[i - 1]) * int(inputs[i + 1])
        inputs.pop(i + 1)
        inputs.pop(i)
        inputs.pop(i - 1)
        inputs.insert(i - 1, value)

    return int(inputs[0])


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
start = perf_counter()
content = read_input("day_18.txt")

# Problem 1
total = 0
for line in content:
    value = solve_equation(line, solve_substring_left_to_right)
    print(f"{line} = {value}")
    total += value
print(total)

# Problem 2
total = 0
for line in content:
    value = solve_equation(line, solve_substring_with_precedence)
    print(f"{line} = {value}")
    total += value
print(total)

end = perf_counter()
print(end - start)

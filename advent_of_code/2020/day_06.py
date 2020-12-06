"""Day 6 challenge"""


# Built-in
from collections import Counter

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
def merge_group_answers_with_count(file_content):
    """
    Merges the group answers together and count the number of people in each group
    :param [str] file_content: Content from the input file
    :return: For each group, a long string of all the answers and the number of people
    :rtype: [(str, int)]
    """
    group_info = []
    merged_answer = ""
    people = 0
    for line in file_content:
        if line != "":
            merged_answer += f"{line}"
            people += 1
        else:
            group_info.append((merged_answer, people))
            merged_answer = ""
            people = 0
    group_info.append((merged_answer, people))  # Adding the last one
    return group_info


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
content = read_input("day_06.txt")
group_data = merge_group_answers_with_count(content)

# Problem 1
total = sum([len(set(answers)) for answers, _ in group_data])
print(total)

# Problem 2
total = 0
for answers, group_size in group_data:
    counter = Counter(answers)
    counter = {
        letter: count for letter, count in counter.items() if count >= group_size
    }
    total += len(counter)
print(total)

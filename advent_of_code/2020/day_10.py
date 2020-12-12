"""Day 10 challenge"""


# Built-in
from time import perf_counter

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
# Setup
adapters = [int(value) for value in read_input("day_10.txt")]
adapters.insert(0, 0)
adapters.sort()

# Problem 1
diffs = {}
for i in range(len(adapters) - 1):
    current_adapter = adapters[i]
    next_adapter = adapters[i + 1]
    delta = next_adapter - current_adapter
    diffs[delta] = diffs.get(delta, 0) + 1
diffs[3] = diffs.get(3, 0) + 1
print(diffs)
print(diffs[1] * diffs[3])

# Problem 2
routes_by_increments = [1]
for i in range(1, len(adapters)):
    possible_routes = 0
    min_ = i - 3 if i > 3 else 0
    # Loop over the 3 previous and closest adapters to see if they can reach this one
    for j in range(min_, i):
        current_adapter = adapters[i]
        previous_adapter = adapters[j]
        # If a new route is possible, it means we can create a new branch from here
        # So we can add to our current total the number of routes this adapter previously had
        if previous_adapter >= current_adapter - 3:
            possible_routes += routes_by_increments[j]
    routes_by_increments.append(possible_routes)
start = perf_counter()
print(routes_by_increments[-1])
print(perf_counter() - start)

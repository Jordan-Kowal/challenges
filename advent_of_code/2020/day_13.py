"""Day 13 challenge"""

# Built-in
from functools import reduce
from math import gcd

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Bus:
    def __init__(self, id_, delta):
        self.id = id_
        self.delta = delta

    def closest_to_timestamp(self, timestamp):
        loop = timestamp // self.id
        if timestamp % self.id != 0:
            loop += 1
        pickup_timestamp = loop * self.id
        return loop, pickup_timestamp

    def timestamp_is_possible(self, timestamp):
        return not timestamp % self.id


def parse_input(content):
    earliest_departure = int(content[0])
    buses = []
    for index, value in enumerate(content[1].split(",")):
        if value == "x":
            continue
        value = int(value)
        buses.append(Bus(value, index))
    return earliest_departure, buses


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
content = read_input("day_13.txt")
earliest_departure, buses = parse_input(content)

# Problem 1
best_bus = None
best_timestamp = None
for bus in buses:
    _, pickup_timestamp = bus.closest_to_timestamp(earliest_departure)
    if best_timestamp is None or pickup_timestamp < best_timestamp:
        best_bus = bus
        best_timestamp = pickup_timestamp
print(best_bus.id * (best_timestamp - earliest_departure))  # 161

# Problem 2
# ------------------ Brute force that took way too long ------------------
# found = False
# slowest_bus = sorted(buses, key=lambda x: x.id)[-1]
# i = 0
# while not found:
#     timestamp = slowest_bus.id * i - slowest_bus.delta
#     for bus in buses:
#         target_timestamp = timestamp + bus.delta
#         if target_timestamp % bus.id > 0:
#             break
#     else:
#         found = True
#     i += 1
# print(timestamp)
# ------------------------------------------------------------------------

# Totally stolen from rosettacode
#   Googled "number divided several different modulo"
#   Found https://math.stackexchange.com/questions/2466179/modular-arithmetic-with-different-mods
#   One comment linked to https://en.wikipedia.org/wiki/Chinese_remainder_theorem
#   Googled it to find how to implement and found rosettacode


def chinese_remainder(n, a):
    sum = 0
    prod = reduce(lambda a, b: a * b, n)
    for n_i, a_i in zip(n, a):
        p = prod // n_i
        sum += a_i * mul_inv(p, n_i) * p
    return sum % prod


def mul_inv(a, b):
    b0 = b
    x0, x1 = 0, 1
    if b == 1:
        return 1
    while a > 1:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += b0
    return x1


numbers = [bus.id for bus in buses]
deltas = [bus.id - bus.delta for bus in buses]
print(chinese_remainder(numbers, deltas))

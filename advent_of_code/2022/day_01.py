# Third-party
from _shared import read_input


class Elf:
    def __init__(self, calories: int):
        self.calories = calories

    def __gt__(self, other: "Elf") -> bool:
        return self.calories > other.calories


content = read_input("day_01.txt")
elves = []
calories = 0
for line in content:
    if line == "":
        elves.append(Elf(calories))
        calories = 0
        continue
    calories += int(line)

print(max(elves).calories)

elves.sort(reverse=True)
print(elves[0].calories + elves[1].calories + elves[2].calories)

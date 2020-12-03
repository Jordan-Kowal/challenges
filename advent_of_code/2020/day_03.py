"""Day 3 challenge"""


# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
grid = [list(line) for line in read_input("day_03.txt")]
height = len(grid)
width = len(grid[0])
slopes = [[1, 1], [3, 1], [5, 1], [7, 1], [1, 2]]
injury_multiplier = 1

for x_add, y_add in slopes:
    injuries = 0
    x, y = 0, 0
    for i in range(height):
        x = x + x_add - ((x + x_add) // width) * width  # 0 <= X <= width-1
        y += y_add
        # We've reached the end or beyond
        if y >= height:
            break
        # Did we land on a tree?
        if grid[y][x] == "#":
            injuries += 1

    print(injuries)
    injury_multiplier *= injuries

print(injury_multiplier)

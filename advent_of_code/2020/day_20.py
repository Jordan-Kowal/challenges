"""Day 20 challenge"""

# Built-in
import re
from time import perf_counter

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Camera:
    def __init__(self, id, photo_grid):
        self.id = id
        self.grid = photo_grid
        self.def_grid = None
        self.cut_def_grid = None
        self.size = len(self.grid)
        self.possible_neighbors = set()
        self.generate_grid_variations()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Camera(id:{self.id})"

    def compute_def_grid_left_match(self, left_camera):
        length_iter = list(range(self.size))
        border_to_match = "".join([left_camera.def_grid[i][-1] for i in length_iter])
        # print(self, left_camera)
        # print(border_to_match)
        for grid in self.grids:
            left_border = "".join([grid[i][0] for i in length_iter])
            # print(left_border)
            if left_border == border_to_match:
                self.def_grid = grid
                break

    def compute_cut_def_grid(self):
        temp = [list(row) for row in self.def_grid.copy()]
        temp = temp[1:-1]  # delete first and last row
        result = []
        for row in temp:
            result.append(row[1:-1])
        result = ["".join(row) for row in result]
        self.cut_def_grid = result

    def compute_def_grid_top_match(self, top_camera):
        border_to_match = "".join(top_camera.def_grid[-1])
        # print(self, top_camera)
        # print(border_to_match)
        for grid in self.grids:
            top_border = "".join(grid[0])
            # print(top_border)
            if top_border == border_to_match:
                self.def_grid = grid
                break

    def get_all_possible_borders(self):
        all_borders = [get_grid_borders_as_string(grid) for grid in self.grids]
        all_borders_flattened = [x for borders in all_borders for x in borders]
        return set(all_borders_flattened)

    def find_possible_neighbors(self, cameras):
        valid_neighbors = set()
        possible_borders = self.get_all_possible_borders()
        for camera in cameras:
            if camera.id == self.id:
                continue
            camera_borders = camera.get_all_possible_borders()
            for border in possible_borders:
                if border in camera_borders:
                    valid_neighbors.add(camera)
                    break
        self.possible_neighbors = valid_neighbors

    def generate_grid_variations(self):
        grids = []
        grid_1 = self.grid
        grid_2 = rotate_grid_90_deg(self.grid)
        grid_3 = rotate_grid_90_deg(grid_2)
        grid_4 = rotate_grid_90_deg(grid_3)
        for grid in [grid_1, grid_2, grid_3, grid_4]:
            top_flipped = top_flip_grid_of_strings(grid)
            # both_flipped = top_flip_grid_of_strings(side_flipped)
            # grids.extend([grid, top_flipped, side_flipped, both_flipped])
            grids.append(grid)
            grids.append(top_flipped)
        self.grids = grids

    @classmethod
    def from_file_content(cls, lines):
        title = lines[0]
        match = re.fullmatch(r"Tile (\d+):", title)
        camera_id = int(match.group(1))
        grid = [photo_line for photo_line in lines[1:]]
        return cls(camera_id, grid)


def get_grid_borders_as_string(grid):
    length = len(grid)
    return (
        "".join(grid[0]),
        "".join(grid[-1]),
        "".join([grid[i][0] for i in range(length)]),
        "".join([grid[i][-1] for i in range(length)]),
    )


def mirror_from_grid(grid):
    grid_mirror = [row.copy() for row in grid.copy()]
    grid_copy = [row.copy() for row in grid.copy()]
    for i, row in enumerate(grid_copy):
        for j, value in enumerate(row):
            grid_mirror[j][i] = value
    return grid_mirror


def top_flip_grid_of_strings(grid):
    grid = [list(row) for row in grid]
    grid_copy = grid.copy()
    for i in range(len(grid)):
        grid_copy[i] = grid[len(grid) - 1 - i]
    return ["".join(row) for row in grid_copy]


def side_flip_grid_of_strings(grid):
    grid = [list(row) for row in grid]
    grid_copy = grid.copy()
    for i, row in enumerate(grid):
        for j, value in enumerate(row):
            grid_copy[i][j] = grid[i][len(row) - 1 - j]
    return ["".join(row) for row in grid_copy]


def rotate_grid_90_deg(grid):
    grid_copy = grid.copy()
    reverted = list(zip(*reversed(grid_copy)))
    return ["".join(row) for row in reverted]


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
# Initialization
start = perf_counter()
content = read_input("day_20.txt")

# Build cameras
cameras = []
acc = []
line_count = len(content)
for i, line in enumerate(content):
    if i + 1 == line_count:
        acc.append(line)
        camera = Camera.from_file_content(acc)
        cameras.append(camera)
    if line == "":
        camera = Camera.from_file_content(acc)
        cameras.append(camera)
        acc = []
    else:
        acc.append(line)

# >>> Problem 1
for camera in cameras:
    camera.find_possible_neighbors(cameras)
corner_camera_ids = [c.id for c in cameras if len(c.possible_neighbors) == 2]

# >>> Problem 2:
# COMPUTE THE GRID PLACEMENTS
corner_cameras = [c for c in cameras if len(c.possible_neighbors) == 2]
start_camera = corner_cameras[0]
for start_grid_index in range(len(start_camera.grids)):
    try:
        camera_map = {camera.id: camera for camera in cameras}
        grid = []
        row_grid = []
        row = 0
        col = 0
        last_camera = None
        last_row_index = None  # Computed at the end of the first row
        while len(camera_map) > 0:
            # --- First turn ---
            if len(grid) == 0 and len(row_grid) == 0:
                start_camera.def_grid = start_camera.grids[start_grid_index]
                row_grid.append(start_camera)
                del camera_map[start_camera.id]
                last_camera = start_camera
                col += 1
                continue

            remaining_neighbors = [
                c for c in last_camera.possible_neighbors if c.id in camera_map
            ]

            # --- First or last row ---
            if row == 0 or row == last_row_index:
                next_camera = [
                    c for c in remaining_neighbors if len(c.possible_neighbors) <= 3
                ][0]

                if len(row_grid) == 0:
                    next_camera.compute_def_grid_top_match(last_camera)
                else:
                    next_camera.compute_def_grid_left_match(row_grid[col - 1])

                # Not the corner yet
                if len(next_camera.possible_neighbors) == 3:
                    row_grid.append(next_camera)
                    del camera_map[next_camera.id]
                    last_camera = next_camera
                    col += 1
                    continue
                # We've reached the corner, but start or end?
                if len(next_camera.possible_neighbors) == 2:
                    row_grid.append(next_camera)
                    del camera_map[next_camera.id]
                    # Start of the line
                    if col == 0:
                        last_camera = next_camera
                        col += 1
                        continue
                    # End of the line
                    else:
                        grid.append(row_grid)
                        last_camera = row_grid[0]
                        last_row_index = int(len(cameras) / len(row_grid)) - 1
                        row_grid = []
                        row += 1
                        col = 0
                        continue
            # --- Middle row ---
            # Start of the line
            if col == 0:
                next_camera = remaining_neighbors[0]
                next_camera.compute_def_grid_top_match(last_camera)
                last_camera = next_camera
                row_grid.append(next_camera)
                del camera_map[next_camera.id]
                col += 1
                continue
            # Rest
            else:
                above_camera = grid[row - 1][col]
                next_camera = [
                    c for c in above_camera.possible_neighbors if c.id in camera_map
                ][0]

                if len(row_grid) == 0:
                    next_camera.compute_def_grid_top_match(last_camera)
                else:
                    next_camera.compute_def_grid_left_match(row_grid[col - 1])

                row_grid.append(next_camera)
                del camera_map[next_camera.id]
                # Not the end of the line
                if len(next_camera.possible_neighbors) == 4:
                    col += 1
                    last_camera = next_camera
                # End of the line
                else:
                    last_camera = row_grid[0]
                    col = 0
                    row += 1
                    grid.append(row_grid)
                    row_grid = []
                continue
        print("FOUND A VALID PATTERN")
        break
    except Exception as e:
        print(e)
        continue

# Remove the borders of each tile for the valid grid
for row in grid:
    for camera in row:
        camera.compute_cut_def_grid()

# We might have built the grid invertedly, so just in case let's handle both cases
grid_mirror = mirror_from_grid(grid)

# Merge tile rows together
photo_height = len(grid[0][0].cut_def_grid)
text_rows = []
for row in grid:
    for i in range(photo_height):
        text = ""
        for camera in row:
            text += camera.cut_def_grid[i]
        text_rows.append(text)
mirror_text_rows = []
for row in grid_mirror:
    for i in range(photo_height):
        text = ""
        for camera in row:
            text += camera.cut_def_grid[i]
        mirror_text_rows.append(text)

# Create all text variations by rotating and flipping
text_variations = []
text_1 = text_rows.copy()
text_2 = rotate_grid_90_deg(text_1)
text_3 = rotate_grid_90_deg(text_2)
text_4 = rotate_grid_90_deg(text_3)
mirror_1 = mirror_text_rows.copy()
mirror_2 = rotate_grid_90_deg(mirror_1)
mirror_3 = rotate_grid_90_deg(mirror_2)
mirror_4 = rotate_grid_90_deg(mirror_3)
for variation in [
    text_1,
    text_2,
    text_3,
    text_4,
    mirror_1,
    mirror_2,
    mirror_3,
    mirror_4,
]:
    top_flipped = top_flip_grid_of_strings(variation)
    variation = [list(row) for row in variation.copy()]
    top_flipped = [list(row) for row in top_flipped.copy()]
    text_variations.append(variation)
    text_variations.append(top_flipped)

# The relative indexes to look for, for the pattern
INDEXES_TO_CHECK = (
    (0, 0),
    (-18, 1),
    (-13, 1),
    (-12, 1),
    (-7, 1),
    (-6, 1),
    (-1, 1),
    (0, 1),
    (1, 1),
    (-17, 2),
    (-14, 2),
    (-11, 2),
    (-8, 2),
    (-5, 2),
    (-2, 2),
)

# One of our text should have the pattern (once or more)
valid_texts = []
for text in text_variations:
    found = False
    x_max = len(text)
    y_max = len(text[0])
    x = 0
    y = 0
    for x in range(x_max):
        for y in range(y_max):
            value = text[x][y]
            if value == "#":
                for a, b in INDEXES_TO_CHECK:
                    new_x = x + b
                    new_y = y + a
                    try:
                        if new_y > 0 and new_x > 0 and text[new_x][new_y] == "#":
                            continue
                        else:
                            break
                    except Exception as e:
                        break
                else:
                    for a, b in INDEXES_TO_CHECK:
                        new_x = x + b
                        new_y = y + a
                        text[new_x][new_y] = "O"
                        found = True
    if found:
        valid_texts.append(text)

# Lets view the results
for text in valid_texts:
    print()
    for row in text:
        print("".join(row))
    print(sum([row.count("#") for row in text]))


# Terminate
end = perf_counter()
print(end - start)

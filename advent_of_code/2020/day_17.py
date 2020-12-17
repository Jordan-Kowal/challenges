"""Day 17 challenge"""


# Built-in
from itertools import product

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Grid:
    def __init__(self, cubes, width):
        """
        Creates a grid with stupid cubes
        :param {Cubes} cubes: Initial cubes that make the grid
        :param width: The length of the x or y dimension
        """
        self.cubes = {cube.coordinates: cube for cube in cubes}
        self.width = width
        self.cycle = 0

    def run_cycles(self, n):
        """
        Run N cycle of the grid, meaning we expand the grid each time and update our cubes
        :param int n: Number of cycles to run
        """
        for i in range(n):
            self.cycle += 1
            self.expand()
            self.update_cubes()
            active_cubes = [cube for cube in self.cubes.values() if cube.active]
            print(len(self.cubes), len(active_cubes))

    def expand(self):
        """
        Increase all of our grid dimension by 2, as if we were wrapping it in a bigger grid
        Generates and stores all the new cubes, which start as inactive
        """
        self.width += 2
        # Expansion happens from both sides of each expansion
        length_range = self.width - 1 if self.width % 2 else self.width
        min_ = -int(length_range / 2)
        max_ = int(length_range / 2)
        possible_x_values = list(range(min_, max_ + 1))
        all_coordinates = set(product(possible_x_values, repeat=4))
        # Now we create the missing cubes following the expansion
        existing_coordinates = set(self.cubes.keys())
        for coordinates in all_coordinates:
            if coordinates not in existing_coordinates:
                x, y, z, w = coordinates
                self.cubes[(x, y, z, w)] = Cube(x, y, z, w, False)

    def update_cubes(self):
        """For each of our cube, computes the next state and then update them"""
        for cube in self.cubes.values():
            cube.compute_next_state(self)
        for cube in self.cubes.values():
            cube.update()


class Cube:
    def __init__(self, x, y, z, w, active):
        """
        Stupid and annoying cube lost in space
        :param int x: X coordinates of the cube
        :param int y: Y coordinates of the cube
        :param int z: Z coordinates of the cube
        :param int w: W coordinates of the cube
        :param bool active: Whether the cube starts active
        """
        self.coordinates = (x, y, z, w)
        self.active = active
        self.neighbor_coordinates = self.compute_neighbor_coordinates()
        self.neighbors = set()
        self.state_will_change = False

    def compute_neighbor_coordinates(self):
        """
        Generates all coordinates within 1 of any of our cube's dimensions
        :return: Set of (x, y, z, w) coordinates
        :rtype: set
        """
        coordinates = set()
        x, y, z, w = self.coordinates
        for x_delta, y_delta, z_delta, w_delta in product([-1, 0, 1], repeat=4):
            if x_delta == y_delta == z_delta == w_delta == 0:
                continue
            else:
                coordinates.add((x + x_delta, y + y_delta, z + z_delta, w + w_delta))
        return coordinates

    def compute_next_state(self, grid):
        """
        Based on our neighbors in the grid, compute our next active state
        :param Grid grid: The grid that holds our neighbors
        """
        self.find_neighbors(grid)
        active_neighbors_count = len([cube for cube in self.neighbors if cube.active])
        # Active changes if not 2 or 3 active neighbors
        if self.active and not (2 <= active_neighbors_count <= 3):
            self.state_will_change = True
            return
        # Inactive changes if 3 active neighbors
        if not self.active and active_neighbors_count == 3:
            self.state_will_change = True
            return

    def find_neighbors(self, grid):
        """
        Finds our neighbor cube instances in the grid and store them
        If we already have all of our neighbors, does nothing
        :param Grid grid: The grid that holds our neighbors
        """
        if len(self.neighbors) < 80:
            neighbors = set()
            for coordinates in self.neighbor_coordinates:
                if coordinates in grid.cubes:
                    neighbors.add(grid.cubes[coordinates])
            self.neighbors = neighbors

    def update(self):
        """Inverts the 'active' property only if necessary"""
        if self.state_will_change:
            self.active = not self.active
            self.state_will_change = False


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
content = read_input("day_17.txt")

# Creates the cubes with the right coordinates
# We make sure our coordinates are centered around 0
length = len(content)
length_range = length - 1 if length % 2 else length
min_ = -int(length / 2)
max_ = int(length / 2)
cubes = set()
for x, line in zip(range(min_, max_ + 1), content):
    for y, char in zip(range(min_, max_ + 1), line):
        active = char == "#"
        cube = Cube(x, y, 0, 0, active)
        cubes.add(cube)

# Run the program
grid = Grid(cubes, len(content))
grid.run_cycles(6)

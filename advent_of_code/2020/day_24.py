"""Day 24 challenge"""

# Built-in
import re
from enum import Enum
from time import perf_counter

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
LINE_REGEX = r"(se|sw|ne|nw|e|w)"
COORDINATES_VALUES = {
    "ne": (0.5, 0.5),
    "e": (1, 0),
    "se": (0.5, -0.5),
    "sw": (-0.5, -0.5),
    "w": (-1, 0),
    "nw": (-0.5, 0.5),
}


class TileColor(Enum):
    """Enum for tile colors"""

    WHITE = "white"
    BLACK = "black"


class Tile:
    """Hexagonal tile that can be flipped on its white or black side"""

    def __init__(self, x, y):
        """
        Creates a tile at the specific coordinates
        Coordinates jump by 0.5 because it is an hexagonal grid
        :param int x: The X coordinate on the grid
        :param int y: The Y coordinate on the grid
        """
        self.color = TileColor.WHITE
        self.coordinates = (x, y)
        self.neighbor_coordinates = [
            (x + dx, y + dy) for dx, dy in COORDINATES_VALUES.values()
        ]
        self.next_color = None

    def flip(self):
        """Changes the color of the current tile by flipping it"""
        if self.color == TileColor.WHITE:
            self.color = TileColor.BLACK
        else:
            self.color = TileColor.WHITE

    def apply_next_color(self):
        """Maybe changes the color of the tile based on its state"""
        if self.next_color is not None:
            self.color = self.next_color
            self.next_color = None


class Grid:
    """Grid with a bunch of hexagonal tiles"""

    def __init__(self):
        """Initializes the grid"""
        self.tile_map = {}
        self.current_coordinates = (0, 0)

    @property
    def black_tile_count(self):
        """
        :return: The number of black tiles in the grid
        :rtype: int
        """
        return len(
            [tile for tile in self.tile_map.values() if tile.color == TileColor.BLACK]
        )

    def daily_flips(self):
        """
        Flips the tile daily based on q certain set of rules
            First, we register all the neighbors of our tiles
            Then, we check which should be flipped based on our rules
            Finally, we flip them all
        """
        # Register missing neighbors
        known_tiles = list(self.tile_map.values())
        for tile in known_tiles:
            for coordinates in tile.neighbor_coordinates:
                if coordinates not in self.tile_map:
                    tile = Tile(*coordinates)
                    self.tile_map[tile.coordinates] = tile
        # Should I flip it
        for tile in self.tile_map.values():
            neighbor_tiles = [
                self.tile_map[coordinates]
                for coordinates in tile.neighbor_coordinates
                if self.tile_map.get(coordinates, None) is not None
            ]
            black_tiles = [t for t in neighbor_tiles if t.color == TileColor.BLACK]
            black_tiles_count = len(black_tiles)
            if tile.color == TileColor.BLACK:
                if black_tiles_count not in {1, 2}:
                    tile.next_color = TileColor.WHITE
            else:
                if black_tiles_count == 2:
                    tile.next_color = TileColor.BLACK
        # Better flip it
        for tile in self.tile_map.values():
            tile.apply_next_color()

    def flip_tile(self, string_coordinates):
        """
        Parses the string coordinates, and flip the tile there
        Registers the tile in the grid if it wasn't in there already
        :param str string_coordinates: Directions concatenated into a string
        """
        coordinates = self.parse_coordinates(string_coordinates)
        if coordinates in self.tile_map:
            tile = self.tile_map[coordinates]
        else:
            tile = Tile(*coordinates)
            self.tile_map[tile.coordinates] = tile
        tile.flip()

    def parse_coordinates(self, string_coordinates):
        """
        Reads the raw string input and translates it into X,Y coordinates
        :param str string_coordinates: Directions concatenated into a string
        :return: The X,Y coordinates of the tile
        :rtype: int, int
        """
        x, y = self.current_coordinates
        for match in re.finditer(LINE_REGEX, string_coordinates):
            text = match.group(1)
            x_temp, y_temp = COORDINATES_VALUES[text]
            x += x_temp
            y += y_temp
        return x, y


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
# Initialization
start = perf_counter()
content = read_input("day_24.txt")

# --------------------------------------------------
# Problem 1:
# --------------------------------------------------
grid = Grid()
for line in content:
    grid.flip_tile(line)
print(grid.black_tile_count)

# --------------------------------------------------
# Problem 2:
# --------------------------------------------------
for i in range(100):
    grid.daily_flips()
print(grid.black_tile_count)

# Terminate
end = perf_counter()
print(end - start)

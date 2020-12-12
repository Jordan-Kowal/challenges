"""Day 11 challenge"""


# Built-in
from enum import Enum

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Grid:
    def __init__(self, grid):
        """
        Creates a grid from a list of spots
        Then updates the spot instances by computing their adjacent spots
        :param [[Spot]] grid: 2d array for Seat instances
        """
        self.grid = grid
        self.x_max = len(self.grid[0]) - 1
        self.y_max = len(self.grid) - 1
        self.compute_adjacent_spots()
        self.compute_visible_seats()

    def __getitem__(self, item):
        """
        :param tuple item: Expects (x, y) coordinates
        :return: The spot instance at the (x, y) coordinates
        :rtype: Spot
        """
        x, y = item
        return self.grid[y][x]

    def reset(self):
        """Every spot that was OCCUPIED is now set to EMPTY"""
        for spot in self.spots:
            if spot.status == Spot.Status.OCCUPIED:
                spot.status = Spot.Status.EMPTY

    def compute_adjacent_spots(self):
        """
        Registers the adjacent spots of each spot from the grid
        Includes diagonally-adjacent spots
        """
        for spot in self.spots:
            spot_x, spot_y = spot.pos
            spot_x_min = 0 if spot_x == 0 else spot_x - 1
            spot_x_max = self.x_max if spot_x == self.x_max else spot_x + 1
            spot_y_min = 0 if spot_y == 0 else spot_y - 1
            spot_y_max = self.y_max if spot_y == self.y_max else spot_y + 1
            adjacent_spots = [
                self[x, y]
                for x in range(spot_x_min, spot_x_max + 1)
                for y in range(spot_y_min, spot_y_max + 1)
            ]
            adjacent_spots = [
                spot for spot in adjacent_spots if spot.pos != (spot_x, spot_y)
            ]
            spot.adjacent_spots = adjacent_spots

    def compute_visible_seats(self):
        """
        Finds the first/closest actual seat in each direction (8 total) for each seat
        The list of seats is then stored in the Spot instance
        """
        for spot in self.spots:
            closest_visible_seats = []
            left_iter = list(reversed(range(0, spot.x)))
            right_iter = list(range(spot.x + 1, self.x_max + 1))
            top_iter = list(reversed(range(0, spot.y)))
            bottom_iter = list(range(spot.y + 1, self.y_max + 1))
            # Left
            for new_x in left_iter:
                potential_seat = self[new_x, spot.y]
                if potential_seat.is_seat:
                    closest_visible_seats.append(potential_seat)
                    break
            # Right
            for new_x in right_iter:
                potential_seat = self[new_x, spot.y]
                if potential_seat.is_seat:
                    closest_visible_seats.append(potential_seat)
                    break
            # Top
            for new_y in top_iter:
                potential_seat = self[spot.x, new_y]
                if potential_seat.is_seat:
                    closest_visible_seats.append(potential_seat)
                    break
            # Bottom
            for new_y in bottom_iter:
                potential_seat = self[spot.x, new_y]
                if potential_seat.is_seat:
                    closest_visible_seats.append(potential_seat)
                    break
            # Top Left
            for new_x, new_y in zip(left_iter, top_iter):
                potential_seat = self[new_x, new_y]
                if potential_seat.is_seat:
                    closest_visible_seats.append(potential_seat)
                    break
            # Top Right
            for new_x, new_y in zip(right_iter, top_iter):
                potential_seat = self[new_x, new_y]
                if potential_seat.is_seat:
                    closest_visible_seats.append(potential_seat)
                    break
            # Bottom Left
            for new_x, new_y in zip(left_iter, bottom_iter):
                potential_seat = self[new_x, new_y]
                if potential_seat.is_seat:
                    closest_visible_seats.append(potential_seat)
                    break
            # Bottom Right
            for new_x, new_y in zip(right_iter, bottom_iter):
                potential_seat = self[new_x, new_y]
                if potential_seat.is_seat:
                    closest_visible_seats.append(potential_seat)
                    break
            spot.closest_visible_seats = closest_visible_seats

    def problem_1(self):
        """Perform an turn update until nothing changes"""
        while True:
            [spot.guess_next_status("adjacent_spots", 4) for spot in self.spots]
            [spot.apply_next_status() for spot in self.spots]
            if all(not spot.has_changed for spot in self.spots):
                break

    def problem_2(self):
        """Perform an turn update until nothing changes"""
        while True:
            [spot.guess_next_status("closest_visible_seats", 5) for spot in self.spots]
            [spot.apply_next_status() for spot in self.spots]
            if all(not spot.has_changed for spot in self.spots):
                break

    @property
    def spots(self):
        """
        :return: List of all spots from left to right, top to bottom
        :rtype: [Spot]
        """
        return [
            self[x, y] for x in range(self.x_max + 1) for y in range(self.y_max + 1)
        ]

    @classmethod
    def from_file_content(cls, file_content):
        """
        Creates a Grid instance from the daily input file
        :param [str] file_content:
        :return: The generated Grid
        :rtype: Grid
        """
        grid = []
        for y, line in enumerate(file_content):
            row = []
            for x, value in enumerate(line):
                row.append(Spot(value, x, y))
            grid.append(row)
        return cls(grid)


class Spot:
    """Room emplacement where one might be able to seat"""

    class Status(Enum):
        """The status of a spot"""

        EMPTY = "L"
        OCCUPIED = "#"
        FLOOR = "."

    def __init__(self, value, x, y):
        """
        Creates a spot with coordinates and a status
        :param str value: Initial value from the input file for this spot
        :param int x: The X coordinate in a room
        :param int y: The Y coordinate in a room
        """
        self.pos = (x, y)
        self.x, self.y = x, y
        self.status = self.status_map[value]
        self.next_status = None
        self.adjacent_spots = []
        self.closest_visible_seats = []
        self.has_changed = False

    def __repr__(self):
        return f"Seat({self.x, self.y})"

    def apply_next_status(self):
        """Set the next_status as our current status"""
        self.has_changed = self.status != self.next_status
        self.status = self.next_status
        self.next_status = None

    def guess_next_status(self, spot_referential, threshold):
        """
        Based on the current status and the adjacent/visible spots,
        Guesses what the next status for our spot will be.
        However, the current status is not yet updated
        :param str spot_referential: The attribute storing the related seats
        :param int threshold: Amount of related occupied seats for the seat to be freed
        """
        changed = False
        referential = getattr(self, spot_referential)
        # Empty: Becomes taken if all adjacent are empty or floor
        if self.status == self.Status.EMPTY:
            if all(
                spot.status in {self.Status.EMPTY, self.Status.FLOOR}
                for spot in referential
            ):
                self.next_status = self.Status.OCCUPIED
                changed = True
        # Taken: Becomes empty if at least N adjacent are occupied
        if self.status == self.Status.OCCUPIED:
            occupied_spots = [
                spot for spot in referential if spot.status == self.Status.OCCUPIED
            ]
            if len(occupied_spots) >= threshold:
                self.next_status = self.Status.EMPTY
                changed = True
        # Floor: No change
        if self.status == self.Status.FLOOR:
            pass
        # No change
        if not changed:
            self.next_status = self.status

    @property
    def is_seat(self):
        return self.status in {self.Status.EMPTY, self.Status.OCCUPIED}

    @property
    def status_map(self):
        """
        :return: A hashmap that maps string inputs to Status enums
        :rtype: dict
        """
        return {
            "L": self.Status.EMPTY,
            "#": self.Status.OCCUPIED,
            ".": self.Status.FLOOR,
        }


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
file_content = read_input("day_11.txt")
grid = Grid.from_file_content(file_content)

# Problem 1
grid.problem_1()
occupied_spots = [spot for spot in grid.spots if spot.status == Spot.Status.OCCUPIED]
print(len(occupied_spots))
grid.reset()

# Problem 2
grid.problem_2()
occupied_spots = [spot for spot in grid.spots if spot.status == Spot.Status.OCCUPIED]
print(len(occupied_spots))
grid.reset()

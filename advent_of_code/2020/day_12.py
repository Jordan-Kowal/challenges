"""Day 12 challenge"""


# Built-in
import re
from enum import Enum

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Ship:
    CARDINAL_ORDER = ["N", "E", "S", "W"]

    def __init__(self):
        """Creates a ship facing East with a related waypoint"""
        # Ship data
        self.X = 0
        self.Y = 0
        self.facing = "E"
        # Waypoint data
        self.waypoint_X = 10
        self.waypoint_Y = 1
        self.waypoint_ref = "E"

    def apply_instruction(self, line, problem):
        """
        Executes the right actions based on the given instruction
        :param str line: Line from the input file
        :param int problem: The problem part of the AOC challenge
        """
        regex = r"([A-Z])(\d+)"
        match = re.match(regex, line)
        value = int(match.group(2))
        action = self.action_mapping[match.group(1)]
        action(value, problem)

    @property
    def action_mapping(self):
        """
        :return: A dict mapping instruction letter and instance methods
        :rtype: dict
        """
        return {
            "N": self.move_north,
            "S": self.move_south,
            "E": self.move_east,
            "W": self.move_west,
            "L": self.turn_left,
            "R": self.turn_right,
            "F": self.move_forward,
        }

    @property
    def manhattan_distance(self):
        """
        :return: Computes the manhattan distance by adding the X and Y absolute values
        :rtype: int
        """
        return abs(self.X) + abs(self.Y)

    def move_north(self, value, problem):
        """
        ACTION
        P1: Moves the ship north by the given value
        P2: Moves the waypoint, not the ship
        :param int value: Value from the input file
        :param int problem: The part of the AOC problem
        """
        if problem == 1:
            self.Y += value
        elif problem == 2:
            self.waypoint_Y += value

    def move_south(self, value, problem):
        """
        ACTION
        P1: Moves the ship south by the given value
        P2: Moves the waypoint, not the ship
        :param int value: Value from the input file
        :param int problem: The part of the AOC problem
        """
        if problem == 1:
            self.Y -= value
        elif problem == 2:
            self.waypoint_Y -= value

    def move_east(self, value, problem):
        """
        ACTION
        P1: Moves the ship east by the given value
        P2: Moves the waypoint, not the ship
        :param int value: Value from the input file
        :param int problem: The part of the AOC problem
        """
        if problem == 1:
            self.X += value
        elif problem == 2:
            self.waypoint_X += value

    def move_west(self, value, problem):
        """
        ACTION
        P1: Moves the ship west by the given value
        P2: Moves the waypoint, not the ship
        :param int value: Value from the input file
        :param int problem: The part of the AOC problem
        """
        if problem == 1:
            self.X -= value
        elif problem == 2:
            self.waypoint_X -= value

    def turn_left(self, value, problem):
        """
        ACTION
        P1: Changes the cardinal point the ship is facing
        P2: Rotates the waypoint around the ship, changing its coordinates
        :param int value: Value from the input file
        :param int problem: The part of the AOC problem
        """
        if problem == 1:
            reversed_cardinals = list(reversed(self.CARDINAL_ORDER))
            current_index = reversed_cardinals.index(self.facing)
            new_index = (current_index + value // 90) % len(self.CARDINAL_ORDER)
            self.facing = reversed_cardinals[new_index]
        elif problem == 2:
            change_count = value // 90
            for i in range(change_count):
                self.waypoint_X, self.waypoint_Y = -self.waypoint_Y, self.waypoint_X
                mapping = {
                    "N": "W",
                    "W": "S",
                    "S": "E",
                    "E": "N",
                }
                self.waypoint_ref = mapping[self.waypoint_ref]

    def turn_right(self, value, problem):
        """
        ACTION
        P1: Changes the cardinal point the ship is facing
        P2: Rotates the waypoint around the ship, changing its coordinates
        :param int value: Value from the input file
        :param int problem: The part of the AOC problem
        """
        if problem == 1:
            current_index = self.CARDINAL_ORDER.index(self.facing)
            new_index = (current_index + value // 90) % len(self.CARDINAL_ORDER)
            self.facing = self.CARDINAL_ORDER[new_index]
        elif problem == 2:
            change_count = value // 90
            for i in range(change_count):
                self.waypoint_X, self.waypoint_Y = self.waypoint_Y, -self.waypoint_X
                mapping = {
                    "N": "E",
                    "E": "S",
                    "S": "W",
                    "W": "N",
                }
                self.waypoint_ref = mapping[self.waypoint_ref]

    def move_forward(self, value, problem):
        """
        ACTION
        P1: Moves the ship in the direction it is facing (so we simply call the related action)
        P2: Moves the ship N times the distances between the ship and the waypoint
        :param int value: Value from the input file
        :param int problem: The part of the AOC problem
        """
        if problem == 1:
            self.action_mapping[self.facing](value, problem)
        elif problem == 2:
            self.X += self.waypoint_X * value
            self.Y += self.waypoint_Y * value


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
# Problem 1
ship = Ship()
for instruction in read_input("day_12.txt"):
    ship.apply_instruction(instruction, 1)
print(ship.X, ship.Y)
print(ship.manhattan_distance)

# Problem 2
ship = Ship()
for instruction in read_input("day_12.txt"):
    ship.apply_instruction(instruction, 2)
print(ship.X, ship.Y)
print(ship.manhattan_distance)

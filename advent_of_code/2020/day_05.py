"""Day 4 challenge"""


# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Seat:
    def __init__(self, row, col):
        """
        Creates a Seat with a row and a col location
        :param int row: The row number
        :param int col: The col number
        """
        self.row = row
        self.col = col

    @property
    def id(self):
        """
        :return: Computes the unique ID of the seat
        :rtype: int
        """
        return self.row * 8 + self.col

    @property
    def loc(self):
        """
        :return: The row and col numbers
        :rtype: int, int
        """
        return self.row, self.col

    @staticmethod
    def compute_binary_split(inputs, low):
        """
        Splits a list of integer of length 2**n where n is the length the provided input list
        Returns the only remaining value after the consecutive splits
        :param str inputs: List of values to go through. Should only have 2 type of values
        :param str low: The value that means 'keep the bottom part'
        :return: The only remaining value after the consecutive splits
        :rtype: int
        """
        elements = range((2 ** len(inputs)) + 1)
        for value in inputs:
            cut = len(elements) // 2
            elements = elements[:cut] if value == low else elements[cut:]
        return elements[0]

    @classmethod
    def create_from_input_line(cls, line):
        """
        Creates a Seat instance from the input line by parsing it and computing its info
        :param str line: Line from the input file
        :return: The created Seat instance
        :rtype: Seat
        """
        row = cls.compute_binary_split(line[:7], "F")
        col = cls.compute_binary_split(line[7:], "L")
        return Seat(row, col)


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
AVAILABLE_SEATS = {(row, col) for row in range(128) for col in range(8)}

# Problem 1
seats = []
for input_line in read_input("day_05.txt"):
    seat = Seat.create_from_input_line(input_line)
    seats.append(seat)
    AVAILABLE_SEATS.remove(seat.loc)
seats.sort(key=lambda x: x.id, reverse=True)
print(seats[0].id)

# Problem 2
# Removes rows from each end until only 1 seat remains
max_row = 127
i = 0
while len(AVAILABLE_SEATS) > 1:
    mod = i // 2
    row_to_remove = max_row - mod if i % 2 else mod
    AVAILABLE_SEATS = {
        (row, col) for row, col in AVAILABLE_SEATS if row != row_to_remove
    }
    i += 1
row, col = AVAILABLE_SEATS.pop()
print(row * 8 + col)

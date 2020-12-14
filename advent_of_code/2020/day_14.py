"""Day 14 challenge"""

# Built-in
import re
from itertools import product

# Personal
from _shared import read_input

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
MASK_REGEX = r"^mask = (.+)$"
MEMORY_REGEX = r"mem\[(\d+)\] = (\d+)"
LENGTH = 36


class Program:
    """Program to read bitmask instructions"""

    def __init__(self):
        """Simply instantiates the memory and mask attributes"""
        self.reset()

    # ----------------------------------------
    # API
    # ----------------------------------------
    def run(self, instructions, problem):
        """
        Runs a list of instructions. Behavior may vary based on which problem you indicate
        :param [str] instructions: Lines from the daily input file
        :param int problem: The AOC problem to tackle
        """
        program.reset()
        for line in instructions:
            mask_match = re.match(MASK_REGEX, line)
            if mask_match is not None:
                self.update_mask(mask_match.group(1))
            else:
                memory_match = re.match(MEMORY_REGEX, line)
                index = int(memory_match.group(1))
                value = int(memory_match.group(2))
                if problem == 1:
                    self.update_memory_v1(index, value)
                else:
                    self.update_memory_v2(index, value)

    # ----------------------------------------
    # ACTIONS
    # ----------------------------------------
    def update_mask(self, string):
        """
        ACTION - Simply update the current mask
        :param str string: A valid 36-char-long bitmask
        """
        self.mask = string

    def update_memory_v1(self, index, value):
        """
        ACTION - Allocates a value into the memory
        The value is transformed into a 36-bit string, then the mask gets applied
        And the value is transformed back into a base-10 integer
        :param int index: The location in the memory
        :param int value: The value from the instruction
        """
        value_binary_string = bin(value)[2:].rjust(LENGTH, "0")
        value_binary_string = self.apply_mask(value_binary_string, "X")
        updated_value = int(value_binary_string, 2)
        self.memory[index] = updated_value

    def update_memory_v2(self, index, value):
        """
        ACTION - Allocates the value in various memory spots
        The memory index is transformed into 36bit, then updated by the mask
        We then replace Xs by 0/1 to generate all possible indexes and put the value there
        :param int index: The location in the memory
        :param int value: The value from the instruction
        """
        index_binary_string = bin(index)[2:].rjust(LENGTH, "0")
        index_binary_string = self.apply_mask(index_binary_string, "0")
        floating_binary_indexes = self.compute_possible_indexes(index_binary_string)
        for fi in floating_binary_indexes:
            self.memory[int(fi, 2)] = value

    # ----------------------------------------
    # UTILS
    # ----------------------------------------
    def apply_mask(self, binary_string, ignore_char):
        """
        Applies the mask to the binary string
        It will override specific spots in the binary string
        :param str binary_string: The binary string to update
        :param str ignore_char: The char from the mask we can ignore
        :return: The maybe-updated binary string
        :rtype: str
        """
        for i in range(LENGTH):
            mask_char = self.mask[i]
            if mask_char != ignore_char:
                binary_string = binary_string[:i] + mask_char + binary_string[i + 1 :]
        return binary_string

    @staticmethod
    def compute_possible_indexes(binary_string):
        """
        Assuming each X in the binary string can be replaced with 0 or 1
        Generates all possible combinaisons of the string
        :param str binary_string: The initial binary string
        :return: All the valid and generated binary strings (with no X left)
        :rtype: [str]
        """
        count = binary_string.count("X")
        if count == 0:
            return [binary_string]
        else:
            strings = []
            for values in product(["0", "1"], repeat=count):
                string = binary_string
                for value in values:
                    string = string.replace("X", value, 1)
                strings.append(string)
            return strings

    def reset(self):
        """Empties the memory and the mask"""
        self.memory = {}
        self.mask = None


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
instructions = read_input("day_14.txt")
program = Program()

# Problem 1
program.run(instructions, 1)
print(sum(program.memory.values()))

# Problem 2
program.run(instructions, 2)
print(sum(program.memory.values()))

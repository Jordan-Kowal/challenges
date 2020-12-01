"""Shared functions and utilities for all challenges"""

# Built-in
import os

# --------------------------------------------------------------------------------
# > Constants
# -------------------------------------------------------------------------------- 
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(CURRENT_DIR, "inputs")


# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
def read_input(filename):
    """
    Reads and returns the content of the inputs file for a challenge
    :param str filename: The name of the input file
    :return: The content of the file
    :rtype: list
    """
    filepath = os.path.join(INPUT_DIR, filename)
    with open(filepath, "r") as f:
        content = [line.rstrip("\n") for line in f.readlines()]
    return content

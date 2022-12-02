# Built-in
import os
from typing import List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(CURRENT_DIR, "inputs")


def read_input(filename: str) -> List[str]:
    filepath = os.path.join(INPUT_DIR, filename)
    with open(filepath, "r") as f:
        content = [line.rstrip("\n") for line in f.readlines()]
    return content

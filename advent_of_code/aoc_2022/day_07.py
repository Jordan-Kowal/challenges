# Built-in
import os
import re
from typing import Dict, Optional, Union

# Third-party
from _shared import read_input

FileSystemItem = Union["Folder", "File"]


class Folder:
    def __init__(self, name: str, parent_folder: Optional["Folder"] = None) -> None:
        self.parent_folder = parent_folder
        self.name = name
        self.children_map: Dict[str, FileSystemItem] = {}  # Direct children

    @property
    def path(self) -> str:
        if self.parent_folder is None:
            return f"{self.name}"
        return f"{self.parent_folder.path}/{self.name}".replace("//", "/")

    @property
    def size(self) -> int:
        return sum(child.size for child in self.children_map.values())

    def add_child(self, item: FileSystemItem) -> None:
        self.children_map[item.name] = item


class File:
    def __init__(self, folder: "Folder", name: str, size: int) -> None:
        self.folder = folder
        self.name = name
        self.size = size

    @property
    def path(self) -> str:
        return f"{self.folder.path}/{self.name}"


class FileSystem:
    CD_REGEX = re.compile(r"^\$ cd (.+)$")
    LS_REGEX = re.compile(r"^\$ ls$")
    FOLDER_REGEX = re.compile(r"^dir (.+)$")
    FILE_REGEX = re.compile(r"^(\d+) (.+)$")

    def __init__(self) -> None:
        self.root_folder = Folder("/")
        self.path_map: Dict[str, FileSystemItem] = {"/": self.root_folder}
        self.current_folder = self.root_folder

    def parse_input(self, line: str) -> None:
        if match := self.CD_REGEX.match(line):
            arg = match.group(1)
            if arg == "..":
                self.current_folder = self.current_folder.parent_folder
            elif arg == "/":
                self.current_folder = self.root_folder
            else:
                new_path = os.path.join(self.current_folder.path, arg)
                self.current_folder = self.path_map[new_path]  # type: ignore
        elif match := self.LS_REGEX.match(line):
            pass
        elif match := self.FOLDER_REGEX.match(line):
            folder = Folder(match.group(1), self.current_folder)
            self.current_folder.add_child(folder)
            self.path_map[folder.path] = folder
        elif match := self.FILE_REGEX.match(line):
            size, name = match.groups()
            file = File(self.current_folder, name, int(size))
            self.current_folder.add_child(file)
            self.path_map[file.path] = file
        else:
            raise ValueError(f"Unknown line: {line}")


lines = read_input("day_07.txt")[1:]

# P1
fs = FileSystem()
[fs.parse_input(line) for line in lines]  # type: ignore
small_folder_total_size = 0
for item in fs.path_map.values():
    if isinstance(item, Folder) and item.size < 100000:
        small_folder_total_size += item.size
print(small_folder_total_size)

# P2
MAX_SPACE = 70000000
REQUIRED_SPACE = 30000000
lines = read_input("day_07.txt")[1:]
fs = FileSystem()
[fs.parse_input(line) for line in lines]  # type: ignore

missing_space = abs((MAX_SPACE - fs.root_folder.size) - REQUIRED_SPACE)
potential_sizes = []
for item in fs.path_map.values():
    if isinstance(item, Folder) and item.size > missing_space:
        potential_sizes.append(item.size)
potential_sizes.sort()
print(potential_sizes[0], potential_sizes[-1])

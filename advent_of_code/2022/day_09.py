# Built-in
from typing import List, Set, Tuple

# Third-party
from _shared import read_input

Position = Tuple[int, int]


class RopeBound:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0

    @property
    def pos(self) -> Position:
        return self.x, self.y


class RopeHead(RopeBound):
    def move(self, direction: str) -> None:
        if direction == "U":
            self.y += 1
        elif direction == "D":
            self.y -= 1
        elif direction == "L":
            self.x -= 1
        elif direction == "R":
            self.x += 1


class RopeTail(RopeBound):
    def __init__(self, parent_bound: RopeBound) -> None:
        super().__init__()
        self.parent_bound = parent_bound
        self.visited: Set[Position] = {self.pos}

    @property
    def distance(self) -> int:
        return abs(self.parent_bound.x - self.x) + abs(self.parent_bound.y - self.y)

    def maybe_move(self) -> None:
        distance = self.distance
        # Adjacent: No move
        if distance <= 1:
            return
        # Diagonal and adjacent: No move
        if (
            distance == 2
            and self.parent_bound.x != self.x
            and self.parent_bound.y != self.y
        ):
            return
        # Diagonal and not adjacent: Move
        if distance == 3 or distance == 4:
            self.x += 1 if self.parent_bound.x > self.x else -1
            self.y += 1 if self.parent_bound.y > self.y else -1
        # Straight: Move
        else:
            if self.parent_bound.x == self.x:
                self.y += 1 if self.parent_bound.y > self.y else -1
            else:
                self.x += 1 if self.parent_bound.x > self.x else -1
        self.visited.add(self.pos)


class Grid:
    def __init__(self) -> None:
        self.head = RopeHead()
        self.all_tail_positions: Set[Position] = {self.head.pos}
        self.tails: List[RopeTail] = []
        current_bound: RopeBound = self.head
        for _ in range(9):
            new_bound = RopeTail(current_bound)
            self.tails.append(new_bound)
            current_bound = new_bound

    def play_turn(self, line: str) -> None:
        direction, value = line.split(" ")
        for _ in range(int(value)):
            self.head.move(direction)
            for tail in self.tails:
                tail.maybe_move()


data = read_input("day_09.txt")
grid = Grid()
for input_line in data:
    grid.play_turn(input_line)
print(len(grid.tails[-1].visited))

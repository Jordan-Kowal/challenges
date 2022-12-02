# Built-in
from functools import cached_property

# Third-party
from _shared import read_input


class ActionType:
    SCISSORS = "SCISSORS"
    ROCK = "ROCK"
    PAPER = "PAPER"


class Round:
    def __init__(self, line: str) -> None:
        opponent_letter, my_letter = line.split(" ")
        self.opponent_action = Action.from_letter(opponent_letter)
        self.player_action = Action.from_objective_letter(
            self.opponent_action, my_letter
        )
        self.player_score = 0
        self.opponent_score = 0

    def play(self) -> None:
        self.player_score = self.player_action.value
        self.opponent_score = self.opponent_action.value
        if self.player_action > self.opponent_action:
            self.player_score += 6
        elif self.player_action == self.opponent_action:
            self.player_score += 3
            self.opponent_score += 3
        else:
            self.opponent_score += 6


class Action:
    def __init__(self, action_type: str) -> None:
        self.action_type = action_type

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Action):
            return NotImplemented
        return self.action_type == other.action_type

    def __gt__(self, other: "Action") -> bool:
        if self.action_type == ActionType.SCISSORS:
            return other.action_type == ActionType.PAPER
        if self.action_type == ActionType.ROCK:
            return other.action_type == ActionType.SCISSORS
        if self.action_type == ActionType.PAPER:
            return other.action_type == ActionType.ROCK
        raise ValueError(f"Unknown action type: {self.action_type}")

    @cached_property
    def value(self) -> int:
        if self.action_type == ActionType.SCISSORS:
            return 3
        if self.action_type == ActionType.ROCK:
            return 1
        if self.action_type == ActionType.PAPER:
            return 2
        raise ValueError(f"Unknown action type: {self.action_type}")

    @classmethod
    def from_letter(cls, letter: str) -> "Action":
        if letter in {"A", "X"}:
            return Action(ActionType.ROCK)
        if letter in {"B", "Y"}:
            return Action(ActionType.PAPER)
        if letter in {"C", "Z"}:
            return Action(ActionType.SCISSORS)
        raise ValueError(f"Invalid letter: {letter}")

    @classmethod
    def from_objective_letter(cls, opponent_action: "Action", letter: str) -> "Action":
        if letter == "X":
            if opponent_action.action_type == ActionType.SCISSORS:
                return Action(ActionType.PAPER)
            if opponent_action.action_type == ActionType.ROCK:
                return Action(ActionType.SCISSORS)
            if opponent_action.action_type == ActionType.PAPER:
                return Action(ActionType.ROCK)
        elif letter == "Y":
            return Action(opponent_action.action_type)
        elif letter == "Z":
            if opponent_action.action_type == ActionType.SCISSORS:
                return Action(ActionType.ROCK)
            if opponent_action.action_type == ActionType.ROCK:
                return Action(ActionType.PAPER)
            if opponent_action.action_type == ActionType.PAPER:
                return Action(ActionType.SCISSORS)
        raise ValueError(f"Invalid letter: {letter}")


content = read_input("day_02.txt")
rounds = []
for line in content:
    round_ = Round(line)
    round_.play()
    rounds.append(round_)
points = sum([round_.player_score for round_ in rounds])
print(points)

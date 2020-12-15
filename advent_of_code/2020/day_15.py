"""Day 15 challenge"""


# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Game:
    def __init__(self, starting_numbers):
        """
        Creates a game with the given starting numbers
        :param [int] starting_numbers: The numbers said during the first turns
        """
        self.starting_numbers = starting_numbers
        self.reset()

    def play(self, turn_quantity):
        """
        Plays a definite number of turns, including the starting turns
        :param int turn_quantity: Number of turns to play
        """
        self.reset()
        self.play_starting_numbers()
        while self.turn < turn_quantity:
            self.turn += 1
            if self.last_number in self.history_map:
                turn_list = self.history_map[self.last_number]
                if len(turn_list) == 1:
                    self.say_number(0)
                else:
                    n = turn_list[-1] - turn_list[-2]
                    self.say_number(n)
            else:
                self.say_number(0)

    def say_number(self, n):
        """
        The number the player will say
        Updates the `last_number` and adds the turn to this number's history
        :param int n: The number to say
        """
        self.last_number = n
        turn_list = self.history_map.get(n, [])
        turn_list.append(self.turn)
        self.history_map[n] = turn_list

    def play_starting_numbers(self):
        """Plays the starting number of the game by saying them"""
        for value in self.starting_numbers:
            self.turn += 1
            self.say_number(value)

    def reset(self):
        """Resets the game state"""
        self.turn = 0
        self.history_map = {}
        self.last_number = None


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
starting_numbers = [int(value) for value in read_input("day_15.txt")[0].split(",")]
game = Game(starting_numbers)

# Problem 1
game.play(2020)
print(game.last_number)

# Problem 2
game.play(30000000)
print(game.last_number)

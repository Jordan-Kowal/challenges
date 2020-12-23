"""Day 22 challenge"""

# Built-in
from time import perf_counter

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Cup:
    """Cup with a value, positioned in a circle with other cups"""

    def __init__(self, id_):
        """
        Creates a standalone cup, not linked to another cup yet
        :param int id_: ID of the cup
        """
        self.id = id_
        self.next_cup = None

    def __repr__(self):
        """
        :return: String similar to how the cup was created
        :rtype: str
        """
        return f"Cup({self.id})"

    def __str__(self):
        """
        :return: String similar to how the cup was created
        :rtype: str
        """
        return f"Cup({self.id})"

    def get_next_cup(self, n):
        """
        Returns the n-th neighbor of our cup
        :param int n:
        :return: The n-th neighbor to the right (clockwise)
        :rtype: Cup
        """
        cup = self
        for i in range(n):
            cup = cup.next_cup
        return cup


class Game:
    """Game of cup, where you move cups around with specific rules"""

    def __init__(self, cups):
        """
        Creates a game instance with starting cups
        :param [Cup] cups: Ordered list of cups available in the game
        """
        self.cups = cups
        self.cups_map = {cup.id: cup for cup in self.cups}
        self.player_cup = self.cups[0]

    def play(self, n):
        """
        Play a total of n turns
        :param int n: Number of turns to play
        """
        for i in range(n):
            # Keep track of turn number
            if i % 100000 == 0:
                print(i)
            # Remove the next three cups from the circle
            first = self.player_cup.get_next_cup(1)
            second = self.player_cup.get_next_cup(2)
            third = self.player_cup.get_next_cup(3)
            excluded_cups = [first, second, third]
            self.player_cup.next_cup = self.player_cup.get_next_cup(4)
            # Find destination cup
            destination_cup = self.find_destination_cup(excluded_cups)
            # Insert the removed cups
            destination_cup_neighbor = destination_cup.next_cup
            destination_cup.next_cup = first
            third.next_cup = destination_cup_neighbor
            # New current cup
            self.player_cup = self.player_cup.next_cup

    def find_destination_cup(self, excluded_cups):
        """
        Finds the destination cup based on the current state of the game
        :return: The destination cup
        :rtype: Cup
        """
        current_id = self.player_cup.id
        excluded_ids = [cup.id for cup in excluded_cups]
        search_id = current_id - 1
        while True:
            if search_id < 0:
                search_id = MAX_ID
            if search_id not in excluded_ids:
                cup = self.cups_map.get(search_id, None)
                if cup is not None:
                    break
            search_id -= 1
        return cup

    def get_ordered_cups(self, starting_id):
        """
        Gets the ordered list of cups, relative to one specific cup
        :param int starting_id: The cup of reference for the order
        :return: The ordered list of cup, relative to the provided starting cup id
        :rtype: [Cup]
        """
        starting_cup = self.cups_map[starting_id]
        cups = [starting_cup]
        cup = starting_cup
        while True:
            cup = cup.next_cup
            if cup == starting_cup:
                break
            cups.append(cup)
        return cups

    @property
    def results_p1(self):
        """
        :return: An ordered list of cup ids, relative to the cup 1 (without including it)
        :rtype: str
        """
        cups = self.get_ordered_cups(1)
        cup_ids = [str(cup.id) for cup in cups]
        return "".join(cup_ids[1:])

    @property
    def results_p2(self):
        """
        :return: The product of the two neighbors of cup(1)
        :rtype: int
        """
        first_cup = self.cups_map[1]
        return first_cup.get_next_cup(1).id * first_cup.get_next_cup(2).id


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
# Initialization
start = perf_counter()
content = read_input("day_23.txt")

# --------------------------------------------------
# Problem 1:
# --------------------------------------------------
# Build cups
cups = [Cup(int(value)) for value in list(content[0])]
# Create clockwise relationships
for i, cup in enumerate(cups):
    next_index = 0 if i + 1 == len(cups) else i + 1
    next_cup = cups[next_index]
    cup.next_cup = next_cup
# Play game
MAX_ID = max([cup.id for cup in cups])
game = Game(cups)
game.play(100)
print(game.results_p1)

# --------------------------------------------------
# Problem 2: 22 seconds runtime
# --------------------------------------------------
# Build cups
int_list = [int(value) for value in list(content[0])]
max_int = max(int_list)
other_ids = list(range(max_int + 1, 1000001))
cups = [Cup(value) for value in int_list + other_ids]
# Create clockwise relationships
for i, cup in enumerate(cups):
    next_index = 0 if i + 1 == len(cups) else i + 1
    next_cup = cups[next_index]
    cup.next_cup = next_cup
# Play game
MAX_ID = 1000000
game = Game(cups)
game.play(10000000)
print(game.results_p2)

# Terminate
end = perf_counter()
print(end - start)

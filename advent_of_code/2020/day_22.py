"""Day 22 challenge"""

# Built-in
from time import perf_counter

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class Player:
    def __init__(self, id_, cards):
        """
        Creates a new player instance with a deck of cards
        :param int id_: ID of the player
        :param [int] cards: Ordered list of cards
        """
        self.id = id_
        self.cards = cards
        self.last_card_played = None

    def play_card(self):
        """
        Removes the first card from the player's deck and returns it
        :return: First card of the deck
        :rtype: int
        """
        self.last_card_played = self.cards.pop(0)
        return self.last_card_played


class Game:
    def __init__(self, player_1, player_2):
        """
        Game instance with two players
        :param Player player_1:
        :param Player player_2:
        """
        self.p1 = player_1
        self.p2 = player_2
        self.players = {p.id: p for p in [self.p1, self.p2]}
        self.deck_combinations = set()
        self.winner = None
        self.loser = None

    def play_normal_game(self):
        """
        Each turn, both players play their top cards
        Winner gets both card, placing the lowest last
        Game is over when 1 player has no card left
        """
        while len(self.p1.cards) > 0 and len(self.p2.cards) > 0:
            p1_card = self.p1.play_card()
            p2_card = self.p2.play_card()
            if p1_card > p2_card:
                self.p1.cards.append(p1_card)
                self.p1.cards.append(p2_card)
            else:
                self.p2.cards.append(p2_card)
                self.p2.cards.append(p1_card)
        self.winner = self.p1 if len(self.p1.cards) > 0 else self.p2

    def play_recursive_game(self):
        """
        Play a recursive game of card
        A turn result might be decided by a sub-game
        :return: The ids of the winner and the loser
        :rtype: int, int
        """
        while True:
            # 1. No more card
            if len(self.p1.cards) == 0:
                self.winner = self.p2
                self.loser = self.p1
                break
            if len(self.p2.cards) == 0:
                self.winner = self.p1
                self.loser = self.p2
                break
            # 2. Combinations
            p1_card_string = "".join([str(c) for c in self.p1.cards])
            p2_card_string = "".join([str(c) for c in self.p2.cards])
            new_combination = (p1_card_string, p2_card_string)
            if new_combination in self.deck_combinations:
                self.winner = self.p1
                self.loser = self.p2
                break
            self.deck_combinations.add(new_combination)
            # 3. Play cards
            p1_card = self.p1.play_card()
            p2_card = self.p2.play_card()
            # 4. Turn winner might depends on recursive game
            if p1_card <= len(self.p1.cards) and p2_card <= len(self.p2.cards):
                p1_cards_copy = self.p1.cards[:p1_card]
                p2_cards_copy = self.p2.cards[:p2_card]
                p1_copy = Player(1, p1_cards_copy)
                p2_copy = Player(2, p2_cards_copy)
                recursive_game = Game(p1_copy, p2_copy)
                winner_id, loser_id = recursive_game.play_recursive_game()
                turn_winner = self.players[winner_id]
                turn_loser = self.players[loser_id]
            else:
                turn_winner = self.p1 if p1_card > p2_card else self.p2
                turn_loser = self.p2 if turn_winner == self.p1 else self.p1
            # 5. Update the winner's deck
            turn_winner.cards.append(turn_winner.last_card_played)
            turn_winner.cards.append(turn_loser.last_card_played)
        return self.winner.id, self.loser.id

    def final_score(self):
        """
        Calculates the final score of the game
        Multiply each card by its index (starting at one), starting from the bottom
        :return: The sum of each card by its index
        :rtype: int
        """
        return sum([card * (i + 1) for i, card in enumerate(self.winner.cards[::-1])])


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
# Initialization
start = perf_counter()
content = read_input("day_22.txt")

# Create objects
players = []
cards = []
i = 0
for line in content:
    if line == "":
        players.append(Player(i, cards))
    elif line.startswith("Player"):
        i += 1
        cards = []
    else:
        cards.append(int(line))
players.append(Player(i, cards))
game = Game(players[0], players[1])


# --------------------------------------------------
# Problem 1:
# --------------------------------------------------
# game.play_normal_game()
# print(game.final_score())


# --------------------------------------------------
# Problem 2:
# --------------------------------------------------
game.play_recursive_game()
print(game.final_score())


# Terminate
end = perf_counter()
print(end - start)

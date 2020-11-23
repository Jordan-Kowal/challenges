import math
import sys
from collections import namedtuple
from itertools import product
from time import perf_counter

# --------------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------------
BREW_LIMIT = 6
INVENTORY_LIMIT = 10

# --------------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------------
# Resources
COLORS = ["blue", "green", "orange", "yellow"]
RESOURCE_VALUES = {
    "blue": 1,
    "green": 2,
    "orange": 3,
    "yellow": 4,
}

# Spell learning
TURN_TRIGGER = 3
LEARNING_THRESHOLD = 0.4
SPELL_LIMIT = 12

# Spell chain

MAX_CHAIN = 10

# Scoring
SPELL_WEIGHTS = [
    ("normalized_benefits", 10),  # 10
    ("normalized_blue_earnings", 2),  # 4
    ("normalized_blue_tax", 0),  # 2
    ("normalized_difficulty", 2),  # 0
    ("normalized_repeatable", 0),  # 20
]

POTION_WEIGHTS = [
    ("normalized_cost", 0),
    ("normalized_distance", 0),
    ("normalized_points_per_cost", 0),
    ("normalized_turns_to_solve", 3),
    ("normalized_spell_compatibility", 0),
]


# --------------------------------------------------------------------------------
# Special
# --------------------------------------------------------------------------------
class TurnTimer:
    """Class to time a game turn"""

    def __init__(self):
        """Starts the timer"""
        self.start = perf_counter()

    def debug(self, *message):
        debug(f"({self.time} ms)", *message)

    def reset(self):
        self.start = perf_counter()

    @property
    def time(self):
        """
        :return: The elapsed time in ms
        :rtype: float
        """
        return (perf_counter() - self.start) * 1000


# --------------------------------------------------------------------------------
# Players
# --------------------------------------------------------------------------------
class Witch:
    """Player that can brew potions, learn and cast spells, rest, and wait"""

    def __init__(self, turn_info, is_player_one):
        """Instantiates all the properties of a witch player"""
        self.is_player_one = is_player_one
        self.previous_score = 0
        self.previous_action = None
        self.previous_inventory = None
        self.score = 0
        self.inventory = None
        self.brew_count = 0
        self.update(turn_info)

    def update(self, turn_info):
        """Updates the inventory, score, and previous action using the turn info"""
        self._update_inventory(turn_info)
        self._update_score(turn_info)
        self._update_brew_count()
        self._update_spell_generation()

    def play(self):
        """Main algorithm in charge of choosing which action to perform each turn"""
        moves = [
            self.craft_and_end_game,
            self.craft_if_opponent_can_finish,
            self.craft_target_potion,
            # self.target_potion_solved,
            self.cast_spell_for_target_potion_if_close,
            self.maybe_learn_spell,
            self.cast_spell_for_target_potion,
            self.rest_to_refresh_required_spells,
            self.brew_a_potion,
            self.cast_random_spell,
            self.learn_random_spell,
            self.dead,
        ]
        action_text = None
        chosen_move = None
        for move in moves:
            action_text = move()
            if action_text is not None:
                chosen_move = move
                break
        print(action_text, chosen_move.__name__)

    # ----------------------------------------
    # Actions
    # ----------------------------------------
    def craft_and_end_game(self):
        """Checks if we can brew a beer, end the game, and win"""
        if self.can_end_game():
            my_best_possible_score = self.compute_best_possible_score()
            opponent_best_possible_score = OPPONENT.compute_best_possible_score()
            if my_best_possible_score >= opponent_best_possible_score:
                return self.brew_best_brewable_potion()
        return

    def craft_if_opponent_can_finish(self):
        """If opponent can craft and end the game, tries to brew something"""
        if OPPONENT.can_end_game():
            return self.brew_best_brewable_potion()
        return

    def craft_target_potion(self):
        """Tries to craft our target potion"""
        target_potion = RANKED_POTIONS[0]
        if self.can_brew(target_potion):
            return f"BREW {target_potion.id}"
        return

    def target_potion_solved(self):
        target_potion = RANKED_POTIONS[0]
        if target_potion.p1_solved:
            return self.cast_spell_for_target_potion()

    def cast_spell_for_target_potion_if_close(self):
        target_potion = RANKED_POTIONS[0]
        turns = target_potion.p1_turns
        if turns <= TURN_TRIGGER and turns != 0:
            return self.cast_spell_for_target_potion()

    def maybe_learn_spell(self):
        """Tries to learn the best grimoire spell if it is worth it"""
        spell_count = len(SPELLS.keys())
        if spell_count < SPELL_LIMIT and len(GRIMOIRE_SPELLS.keys()) > 0:
            limit = math.ceil(spell_count * LEARNING_THRESHOLD)
            spells_to_beat = self.ranked_spells[limit:]
            for spell in SPELL_RANKINGS:
                if spell.is_grimoire:
                    better = all(
                        [
                            spell.score.normalized_score
                            > spell_to_beat.score.normalized_score
                            for spell_to_beat in spells_to_beat
                        ]
                    )
                    if better and self.can_learn(spell):
                        return f"LEARN {spell.id}"
        return

    def cast_spell_for_target_potion(self):
        """Tries to cast a spell to get resource towards our target potion"""
        target_potion = RANKED_POTIONS[0]
        if len(target_potion.p1_spells) > 0:
            spell, qty = target_potion.p1_spells[0]
            if self.can_cast(spell):
                if not spell.repeatable:
                    return f"CAST {spell.id}"
                else:
                    cast_count = 0
                    temp_inventory = self.inventory.copy()
                    while True:
                        temp_inventory = temp_inventory + spell.delta
                        if not temp_inventory.is_valid:
                            break
                        cast_count += 1
                    final_cast_count = min([cast_count, qty])
                    return f"CAST {spell.id} {final_cast_count}"
        return

    @staticmethod
    def rest_to_refresh_required_spells():
        """If we failed to cast due to a spell not being available, REST"""
        target_potion = RANKED_POTIONS[0]
        if len(target_potion.p1_spells) > 0:
            blocked_by_inventory = all(
                spell.castable for spell, _ in target_potion.p1_spells
            )
            if not blocked_by_inventory:
                return "REST"
        return

    def brew_a_potion(self):
        """Tries to brew any potion to make some room in the inventory"""
        return self.brew_best_brewable_potion()

    def cast_random_spell(self):
        """Cast a random spell"""
        for spell in self.ranked_spells:
            if self.can_cast(spell):
                return f"CAST {spell.id}"

    def learn_random_spell(self):
        """Learn a random spell"""
        ranked_grimoire_spells = sorted(
            list(GRIMOIRE_SPELLS.values()),
            key=lambda x: x.score.normalized_score,
            reverse=True,
        )
        for grimoire_spell in ranked_grimoire_spells:
            if self.can_learn(grimoire_spell):
                return f"LEARN {grimoire_spell.id}"

    @staticmethod
    def dead():
        """Better REST than WAIT"""
        return "REST"

    # ----------------------------------------
    # Action helpers
    # ----------------------------------------
    def brew_best_brewable_potion(self):
        """
        Fetches the best brew we can already brew and returns the necessary instruction
        :return: Text to brew a potion or None
        :rtype: str or None
        """
        potion = self.get_best_brewable_potion()
        if potion is not None:
            return f"BREW {potion.id}"
        return

    def can_brew(self, potion):
        """
        Checks if we can brew a potion based on our resources
        :param Potion potion: The potion we might be able to brew
        :return: Whether it's possible
        :rtype: bool
        """
        temp_inventory = self.inventory.copy()
        temp_inventory = temp_inventory + potion.delta
        return temp_inventory.is_valid

    def can_cast(self, spell):
        """
        Checks if a spell is castable and we have room in the inventory
        :param Spell spell: The spell we would like to cast
        :return: Whether we can cast it
        :rtype: bool
        """
        temp_inventory = self.inventory.copy()
        temp_inventory = temp_inventory + spell.delta
        if spell.castable and temp_inventory.is_valid:
            return True
        return False

    def can_end_game(self):
        """
        :return: Whether we can end the game by crafting the last potion
        :rtype: bool
        """
        if self.brew_count == (BREW_LIMIT - 1):
            for potion in RANKED_POTIONS:
                if self.can_brew(potion):
                    return True
        return False

    def can_learn(self, spell):
        """
        Whether a GrimoireSpell can be learnt
        :param GrimoireSpell spell: The spell we want to learn
        :return: Whether we can learn it
        :rtype: bool
        """
        return self.inventory.blue >= spell.blue_tax

    def compute_best_possible_score(self):
        """
        Computes the best possible score by checking the inventory value after maybe brewing a potion
        :return: The best possible score
        :rtype: int
        """
        potion = self.get_best_brewable_potion()
        if potion is not None:
            temp_inventory = self.inventory.copy()
            temp_inventory = temp_inventory + potion.delta
            return self.score + potion.price + temp_inventory.potential_score
        else:
            return self.score + self.inventory.potential_score

    def get_best_brewable_potion(self):
        """
        Fetches the best potion we could brew THIS turn. Returns None if we can't brew anything
        :return: The best potion we could brew this turn
        :rtype: Potion or None
        """
        for potion in RANKED_POTIONS:
            if self.can_brew(potion):
                return potion
        return

    # ----------------------------------------
    # Turn update
    # ----------------------------------------
    def _guess_previous_action(self):
        """
        :return: The last turn action based on the property updates
        :rtype: str
        """
        # BREW
        if self.previous_score != self.score:
            return "BREW"
        # CAST
        has_cast = any([spell.cast_last_turn for spell in self.spells.values()])
        if has_cast:
            return "CAST"
        # REST
        has_rested = any([spell.refreshed_last_turn for spell in self.spells.values()])
        if has_rested:
            return "REST"
        # WAIT
        return "WAIT"

    def _update_brew_count(self):
        """Updates the brew count only if the previous action was BREW"""
        self.previous_action = self._guess_previous_action()
        if self.previous_action == "BREW":
            self.brew_count += 1

    def _update_inventory(self, turn_info):
        """Stores a copy of the previous inventory before updating it"""
        if self.inventory is not None:
            self.previous_inventory = self.inventory.copy()
        self.inventory = Inventory(
            turn_info[0], turn_info[1], turn_info[2], turn_info[3]
        )

    def _update_score(self, turn_info):
        """Simply stores the previous score and updates the current one"""
        self.previous_score = self.score
        self.score = turn_info[4]

    def _update_spell_generation(self):
        delta = Delta(0, 0, 0, 0)
        for spell in self.spells.values():
            delta = delta + spell.delta
        self.generation_delta = delta

    # ----------------------------------------
    # Properties
    # ----------------------------------------
    @property
    def ranked_spells(self):
        """
        :return: List of our spells, ranked from best to worst
        :rtype: list
        """
        spells = list(self.spells.values())
        spells.sort(key=lambda x: x.score.normalized_score, reverse=True)
        return spells

    @property
    def spells(self):
        """
        :return: The right dict that contains the player's spells
        :rtype: dict
        """
        return SPELLS if self.is_player_one else OPPONENT_SPELLS


# --------------------------------------------------------------------------------
# Resource management
# --------------------------------------------------------------------------------
class Delta:
    """Simple class that stores the 4 resources of the game"""

    def __init__(self, blue, green, orange, yellow):
        """Stores the 4 resources in their respective color/name"""
        self.blue = int(blue)
        self.green = int(green)
        self.orange = int(orange)
        self.yellow = int(yellow)

    def __repr__(self):
        """
        :return: Representation of the Delta instance
        :rtype: str
        """
        return f"Delta(blue: {self.blue}, green: {self.green}, orange: {self.orange}, yellow: {self.yellow})"

    def __add__(self, other):
        """
        Adds each resource and returns a new Delta object
        :param Delta other: Any class with the same resource properties
        :return: The new Delta/Inventory instance
        :rtype: Delta or Inventory
        """
        blue = self.blue + other.blue
        green = self.green + other.green
        orange = self.orange + other.orange
        yellow = self.yellow + other.yellow
        return self.__class__(blue, green, orange, yellow)

    def __mul__(self, number):
        """
        Multiplies each resource and returns a new Delta object
        :param int number: The amount to multiply by
        :return: The new Delta/Inventory instance
        :rtype: Delta or Inventory
        """
        blue = self.blue * number
        green = self.green * number
        orange = self.orange * number
        yellow = self.yellow * number
        return self.__class__(blue, green, orange, yellow)

    def __sub__(self, other):
        """
        Subtracts each resource and returns a new Delta object
        :param Delta other: Any class with the same resource properties
        :return: The new Delta/Inventory instance
        :rtype: Delta or Inventory
        """
        blue = self.blue - other.blue
        green = self.green - other.green
        orange = self.orange - other.orange
        yellow = self.yellow - other.yellow
        return self.__class__(blue, green, orange, yellow)

    def copy(self):
        """
        :return: A independent copy of our Delta instance
        :rtype: Delta
        """
        return Delta(self.blue, self.green, self.orange, self.yellow)


class Inventory(Delta):
    """The inventory of a Witch, which contains the 4 resources and can be updated"""

    # ----------------------------------------
    # Utilities
    # ----------------------------------------
    def copy(self):
        """
        :return: An independent copy of our Inventory
        :rtype: Inventory
        """
        return Inventory(*self.resources)

    def potential_score_after_brew(self, potion):
        """
        Computes the potential score of the inventory after a potion is brewed
        :param Potion potion: The potion we could brew
        :return: Sum of the counts of non-blue elements after the brewing
        :rtype: int
        """
        temp_inventory = self.copy()
        temp_inventory + potion.delta
        return temp_inventory.potential_score

    # ----------------------------------------
    # Properties
    # ----------------------------------------
    @property
    def is_full(self):
        """
        :return: Whether the inventory is full
        :rtype: bool
        """
        return sum(self.resources) >= INVENTORY_LIMIT

    @property
    def is_valid(self):
        """
        :return: Whether the inventory is still valid, no resources are negative
        :rtype: bool
        """
        return (
            all(amount >= 0 for amount in self.resources)
            and sum(self.resources) <= INVENTORY_LIMIT
        )

    @property
    def potential_score(self):
        """
        :return: Return the sum of counts of each non-blue element
        :rtype: int
        """
        return sum([self.green, self.orange, self.yellow])

    @property
    def resources(self):
        """
        :return: The four resources in a list
        :rtype: [int, int, int, int]
        """
        return [self.blue, self.green, self.orange, self.yellow]


# --------------------------------------------------------------------------------
# Actions
# --------------------------------------------------------------------------------
class Action:
    """
    Class to parse and register the action provided by the game workflow

    The 'action_info' should return the following elements:
        0 -> the unique ID of this spell or recipe
        1 -> in the first league: BREW; later: CAST, OPPONENT_CAST, LEARN, BREW
        2 -> tier-0 ingredient change
        3 -> tier-1 ingredient change
        4 -> tier-2 ingredient change
        5 -> tier-3 ingredient change
        6 -> the price in rupees if this is a potion
        7 -> in the first two leagues:
            always 0;
            later: the index in the tome if this is a tome spell, equal to the read-ahead tax;
            For brews, this is the value of the current urgency bonus
        8 -> in the first two leagues:
            always 0;
            later: taxed tier-0 ingredients you gain from learning this spell;
            For brews, this is how many times you can still gain an urgency bonus
        9 -> in the first league:
            always 0;
            later: 1 if this is a castable player spell
        10 -> for the first two leagues:
            always 0;
            later: 1 if this is a repeatable player spell
    """

    def __init__(self, action_info):
        """Parses an action by storing its info in various properties"""
        self.id = int(action_info[0])
        self.type = action_info[1]
        self.delta = [action_info[2], action_info[3], action_info[4], action_info[5]]
        self.price = int(action_info[6])
        self.tome_index = int(action_info[7])
        self.tax_count = int(action_info[8])
        self.castable = action_info[9] != "0"
        self.repeatable = action_info[10] != "0"

    def register(self):
        """Registers the action based on its type"""
        if self.type == "BREW":
            self._register_potion()
        if self.type == "CAST":
            self._register_spell()
        if self.type == "OPPONENT_CAST":
            self._register_opponent_spell()
        if self.type == "LEARN":
            self._register_grimoire_spell()

    # ----------------------------------------
    # Private
    # ----------------------------------------
    def _register_grimoire_spell(self):
        """Registers a new grimoire spell or updates an existing one"""
        if not self.id in GRIMOIRE_SPELLS:
            spell = GrimoireSpell(
                self.id, self.delta, self.tome_index, self.tax_count, self.repeatable
            )
            GRIMOIRE_SPELLS[self.id] = spell
        else:
            grimoire_spell = GRIMOIRE_SPELLS[self.id]
            grimoire_spell.update(self.tome_index, self.tax_count)

    def _register_opponent_spell(self):
        """Registers a new spell for the opponent or updates an existing one"""
        if not self.id in SPELLS:
            spell = Spell(self.id, self.delta, self.castable, self.repeatable)
            OPPONENT_SPELLS[self.id] = spell
        else:
            spell = SPELLS[self.id]
            spell.update(self.castable)

    def _register_potion(self):
        """Registers a new potion or updates an existing one"""
        if not self.id in POTIONS:
            potion = Potion(self.id, self.delta, self.price, self.tome_index)
            POTIONS[self.id] = potion
        else:
            potion = POTIONS[self.id]
            potion.update(self.price, self.tome_index)

    def _register_spell(self):
        """Registers a new spell or updates an existing one"""
        if not self.id in SPELLS:
            spell = Spell(self.id, self.delta, self.castable, self.repeatable)
            SPELLS[self.id] = spell
        else:
            spell = SPELLS[self.id]
            spell.update(self.castable)


class Potion:
    """A brewable potion with a cost and a price/score"""

    def __init__(self, potion_id, delta, price, urgency_bonus):
        """
        Creates a potion
        :param int potion_id: The action ID
        :param [int] delta: The values for the 4 resources
        :param int price: The price/score earned when brewing the potion
        :param int urgency_bonus: The bonus point due to the urgency bonus
        """
        self.id = potion_id
        self.delta = Delta(*delta)
        self.update(price, urgency_bonus)

    def __repr__(self):
        """
        :return: Representation of the Potion instance
        :rtype: str
        """
        return (
            f"Potion("
            f"id: {self.id}, "
            f"delta: {self.delta.blue},{self.delta.green},{self.delta.orange},{self.delta.yellow}, "
            f"price: {self.price}"
            f")"
        )

    def update(self, price, urgency_bonus):
        """
        Resets the potion's score and updates its price
        :param int price: The price/score earned when brewing the potion
        :param int urgency_bonus: The bonus point due to the urgency bonus
        """
        self.price = price
        self.urgency_bonus = urgency_bonus
        self.score = None

    def compute_score(self):
        """Instantiate the score which will rank the potion"""
        # self._solve_potion(ME, "p1_solved", "p1_spells", "p1_turns")
        # self._solve_potion(OPPONENT, "p2_solved", "p2_spells", "p2_turns")
        self.score = PotionScore(self)

    def _calculate_improvement(self, witch, temp_inventory):
        """

        :param witch:
        :param temp_inventory:
        :return:
        """
        improvement_qty = 0
        improvement_value = 0
        # Evaluate progress for each color
        for color in COLORS:
            current_value = getattr(witch.inventory, color)
            temp_value = getattr(temp_inventory, color)
            potion_value = abs(getattr(self.delta, color))
            start_diff = current_value - potion_value
            end_diff = temp_value - potion_value
            if start_diff < 0:
                if end_diff <= start_diff:
                    improvement_qty += end_diff - start_diff
                    improvement_value += (end_diff - start_diff) * RESOURCE_VALUES[
                        color
                    ]
                else:
                    if end_diff > 0:
                        improvement_qty += abs(start_diff)
                        improvement_value += abs(start_diff) * RESOURCE_VALUES[color]
                    else:
                        improvement_qty += end_diff - start_diff
                        improvement_value += (end_diff - start_diff) * RESOURCE_VALUES[
                            color
                        ]
            else:
                if end_diff >= 0:
                    pass
                else:
                    improvement_qty += end_diff
                    improvement_value += end_diff * RESOURCE_VALUES[color]
        return improvement_qty, improvement_value

    @staticmethod
    def _calculate_spell_chain_turns(spell_chain):
        """
        NOT EXACT
        :param spell_chain:
        :return:
        """
        turns = 0
        has_rested = 0
        for spell, qty in spell_chain:
            if not spell.castable and not has_rested:
                has_rested = True
                turns += 1
            if spell.repeatable:
                turns += 1
            else:
                turns += qty * 2 - 1
        return turns

    def _compute_distance(self, inventory):
        distance = 0
        for color in COLORS:
            potion_value = abs(getattr(self.delta, color))
            inv_value = getattr(inventory, color)
            if potion_value > inv_value:
                distance += (potion_value - inv_value) * RESOURCE_VALUES[color]
        return distance

    def _evaluate_spell_chain_efficiency(self, witch, spell_chain):
        """

        :param witch:
        :param spell_chain:
        :return:
        """
        # Will be returned
        solved = False
        distance = self._compute_distance(witch.inventory)
        # Try spell chain
        temp_inventory = witch.inventory.copy()
        for spell in spell_chain:
            temp_inventory = temp_inventory + spell.delta
            if not temp_inventory.is_valid:
                return
        else:
            # Did it solve the potion?
            fake_inventory = temp_inventory.copy()
            fake_inventory = fake_inventory + self.delta
            spell_chain = self._reformat_spell_chain(spell_chain)
            turns = self._calculate_spell_chain_turns(spell_chain)
            if fake_inventory.is_valid:
                solved = True
            # If not, what's the progress
            else:
                distance = self._compute_distance(temp_inventory)
            # Returns all the info
            return spell_chain, solved, turns, distance

    def _reformat_spell_chain(self, spell_chain):
        """

        :param spell_chain:
        :return:
        """
        better_spell_chain = []
        previous_spell = None
        for spell in spell_chain:
            if previous_spell == spell:
                _, qty = better_spell_chain[-1]
                better_spell_chain[-1] = (spell, qty + 1)
            else:
                previous_spell = spell
                better_spell_chain.append((spell, 1))
        return better_spell_chain

    def _solve_potion(self, witch, solve_attr, spells_attr, turns_attr):
        """
        Tries all spell chains of (up to) N spells and checks if it can make the potion brewable
        If not, it evaluates how much closer/farther we got from our the potion
        :param Witch witch: The current player to compute for
        :param str solve_attr: Name of the attribute to store whether the potion was solved
        :param str spells_attr: Name of the attribute to store the best spell chain
        :param str turns_attr: Name of the attribute to store the turn amount
        """
        # Maybe we can brew it
        if witch.can_brew(self):
            setattr(self, solve_attr, True)
            setattr(self, spells_attr, [])
            setattr(self, turns_attr, 0)
            return
        # Else let's see which spell chain would be best
        Result = namedtuple("Result", ["spell_chain", "solved", "turns", "distance"],)
        results = []

        spells = list(witch.spells.values())
        spell_quantity = len(spells)
        i = 0
        start = perf_counter()
        end = perf_counter()
        while i < spell_quantity and ((end - start) * 1000 < POTION_LAST_TURN_MS):
            spell_chains = list(product(spells, repeat=i + 1))
            for spell_chain in spell_chains:
                result = self._evaluate_spell_chain_efficiency(witch, spell_chain)
                if result is not None:
                    (spell_chain, solved, turns, distance,) = result
                    result_object = Result(
                        spell_chain=spell_chain,
                        solved=solved,
                        turns=turns,
                        distance=distance,
                    )
                    results.append(result_object)
            i += 1
            end = perf_counter()
        if len(results) > 0:
            solvers = [result for result in results if result.solved]
            if len(solvers) > 0:
                solvers.sort(key=lambda x: x.turns)
                best_result = solvers[0]
            else:
                results.sort(key=lambda x: (x.distance, x.turns), reverse=False)
                best_result = results[0]
            setattr(self, solve_attr, best_result.solved)
            setattr(self, spells_attr, best_result.spell_chain)
            setattr(self, turns_attr, best_result.turns)
        else:
            setattr(self, solve_attr, False)
            setattr(self, spells_attr, [])
            setattr(self, turns_attr, None)


class Spell:
    """A castable spell to generate more resources"""

    def __init__(self, spell_id, delta, castable, repeatable):
        """
        Simply stores the args into the instance
        :param int spell_id:
        :param [int] delta: The 4 resources associated with the spell (positive and negative)
        :param bool castable: Whether the spell can be cast
        :param bool repeatable: Whether the spell is repeatable
        """
        self.cast_last_turn = False
        self.is_grimoire = False
        self.refreshed_last_turn = False
        self.id = spell_id
        self.delta = Delta(*delta)
        self.castable = castable
        self.repeatable = repeatable
        self.blue_tax = 0
        self.blue_earnings = 0

    def __repr__(self):
        """
        :return: Representation of the Spell instance
        :rtype: str
        """
        return (
            f"Spell("
            f"id: {self.id}, "
            f"delta: {self.delta.blue},{self.delta.green},{self.delta.orange},{self.delta.yellow}, "
            f"castable: {self.castable}, "
            f"repeatable: {self.repeatable}"
            f")"
        )

    def update(self, castable):
        """
        Updates a spells and flags whether it has been used or refreshed
        :param bool castable: Whether the spell can be cast
        """
        self.cast_last_turn = self.castable and not castable
        self.refreshed_last_turn = not self.castable and castable
        self.castable = castable

    def compute_score(self):
        """Instantiates the spell score"""
        self.score = SpellScore(self)

    def copy(self):
        """
        Creates a shallow copy of the Spell instance, without its score
        :return: A new Spell instance
        :rtype: Spell
        """
        return Spell(
            self.id,
            [self.delta.blue, self.delta.green, self.delta.orange, self.delta.yellow,],
            self.castable,
            self.repeatable,
        )


class GrimoireSpell:
    """Spell that can be learned from the grimoire"""

    def __init__(self, spell_id, delta, blue_tax, blue_earnings, repeatable):
        """
        Creates a Grimoire Spell
        :param int spell_id: The element unique ID
        :param [int] delta: The values for the 4 resources
        :param int blue_tax: The amount of blue required to purchase
        :param int blue_earnings: The amount of blue ressources earned when learnt
        :param bool repeatable: Whether the spell will be repeatable
        """
        self.id = spell_id
        self.is_grimoire = True
        self.delta = Delta(*delta)
        self.castable = True  # Used for ranking
        self.repeatable = repeatable
        self.update(blue_tax, blue_earnings)

    def __repr__(self):
        """
        :return: Representation of the Spell instance
        :rtype: str
        """
        return (
            f"GrimoireSpell("
            f"id: {self.id}, "
            f"delta: {self.delta.blue},{self.delta.green},{self.delta.orange},{self.delta.yellow}, "
            f"blue_tax: {self.blue_tax}, "
            f"blue_earnings: {self.blue_earnings}, "
            f"repeatable: {self.repeatable}"
            f")"
        )

    def update(self, blue_tax, blue_earnings):
        """Updates the blue_tax and blue_earnings which may change each turn"""
        self.blue_tax = blue_tax
        self.blue_earnings = blue_earnings
        self.score = None

    def compute_score(self):
        """Instantiates the grimoire spell scores"""
        self.score = SpellScore(self)

    def copy(self):
        """
        Creates a shallow copy of the GrimoireSpell instance, without its score
        :return: A new GrimoireSpell instance
        :rtype: GrimoireSpell
        """
        return GrimoireSpell(
            self.id,
            [self.delta.blue, self.delta.green, self.delta.orange, self.delta.yellow,],
            self.blue_tax,
            self.blue_earnings,
            self.repeatable,
        )


# --------------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------------
class SpellChain:
    def __init__(self, starting_inv, potion, spells):
        """

        :param Delta starting_inv:
        :param Potion potion:
        :param [Spell] spells:
        """
        self.spells = spells
        self.potion = potion
        self.inventory = starting_inv.copy()
        self.chain = 0

    def compute_best_path(self):
        # Already craftable
        if self.potion._compute_distance(self.inventory) == 0:
            return [], True, 0
        # Best path for starting with each spell
        best_chains = []
        for spell in self.spells:
            result = self.compute_best_path_from(spell)
            if result is not None:
                spell_chain, solved, turns = result
                best_chains.append((spell_chain, solved, turns))
        # Extract bestest result
        if len(best_chains) > 0:
            best_chains.sort(key=lambda x: x[1], reverse=True)  # solved
            best_chains.sort(key=lambda x: x[2])  # turns
            return best_chains[0]
        return

    def compute_best_path_from(self, starting_spell):
        chain = []
        solved = False

        # First spell
        inventory = self.inventory.copy()
        inventory = inventory + starting_spell.delta
        if not inventory.is_valid:
            return
        else:
            chain.append(starting_spell)
            if self.potion._compute_distance(inventory) == 0:
                solved = True

        # Cast spells and only keep the best one each turn
        i = 0
        while not solved and i < MAX_CHAIN:
            spell_results = []
            for spell in self.spells:
                inventory_copy = inventory.copy()
                inventory_copy = inventory_copy + spell.delta

                if not inventory_copy.is_valid:
                    continue

                new_distance = self.potion._compute_distance(inventory_copy)
                solved = new_distance == 0
                spell_results.append((spell, solved, new_distance))

            spell_results.sort(key=lambda x: x[1], reverse=True)  # solved
            spell_results.sort(key=lambda x: x[2])  # new_distance
            if len(spell_results):
                spell = spell_results[0][0]
                chain.append(spell)
                inventory = inventory + spell.delta
            i += 1
        chain = self.potion._reformat_spell_chain(chain)
        turns = self.potion._calculate_spell_chain_turns(chain)
        return chain, solved, turns


class Score:
    """Parent class for scores with utility functions"""

    def _apply_weights(self, weights):
        """
        Applies weights to our results before merging them
        :return: The merged total after weighting
        :rtype: float
        """
        total = 0
        divider = 0
        for attr_name, weight in weights:
            total += getattr(self, attr_name) * weight
            divider += weight
        return total / divider

    @staticmethod
    def _compute_difficulty(witch, delta):
        """
        Attributes a difficulty level at the spell based on how hard it is to cast
        Evaluates the number of different resources and their value in money
        :param Witch witch: The witch to evaluate the difficulty for
        :param Delta delta: The delta to evaluate
        :return: The difficulty level
        :rtype: int
        """
        difficulty = 0
        for color in COLORS:
            color_value = getattr(delta, color)
            current_quantity = getattr(witch.inventory, color)
            if color_value < 0:
                difficulty += 1
                difficulty += abs(color_value * RESOURCE_VALUES[color])
                if current_quantity < color_value:
                    difficulty += 2
        return difficulty

    @staticmethod
    def _convert_delta_to_money(delta):
        """
        :return: The delta converted into money based on the RESOURCE_VALUES settings
        :rtype: int
        """
        return sum([getattr(delta, color) * RESOURCE_VALUES[color] for color in COLORS])

    def _normalize_attribute(self, attr_name, scores):
        """
        Basic function to normalize an attribute based on the other scores
        :param str attr_name: The attribute to normalize
        :param [Score] scores: List of all available scores
        :return: The normalized value
        :rtype: float
        """
        all_attribute_values = [
            getattr(score, attr_name)
            for score in scores
            if getattr(score, attr_name) is not None
        ]
        max_value = max(all_attribute_values)
        if max_value == 0 or len(all_attribute_values) == 0:
            return 0
        return getattr(self, attr_name) / max_value


class PotionScore(Score):
    """
    Score representation for a potion, allowing us to rank it. Ranks a potion based on:
        The awarded points
        The points per cost/money
        Whether it can be crafted
        How fast it can be craft
        Whether the opponent can steal it from us
    """

    def __init__(self, potion):
        """
        Simply stores all the args into the instance
        :param Potion potion: The potion the score belongs to
        """
        self.potion = potion
        # Spell Chain
        spell_chain_instance = SpellChain(ME.inventory, self.potion, ME.ranked_spells)
        result = spell_chain_instance.compute_best_path()
        spell_chain, solved, turns = result
        self.potion.p1_spells = spell_chain
        self.potion.p1_solved = solved
        self.potion.p1_turns = turns
        self.points = self.potion.price

        self.cost = abs(self._convert_delta_to_money(self.potion.delta))
        self.distance = self.potion._compute_distance(ME.inventory)

        self.points_per_cost = self.points / self.cost
        self.spell_compatibility = self._compute_spell_compatibility(ME)
        self.turns_to_solve = self._compute_turns_to_solve()

    def __repr__(self):
        return f"PotionScore(score: {self.normalized_score}, cost: {self.cost}, distance: {self.distance}, points_per_cost: {self.points_per_cost}, spell_compatibility: {self.spell_compatibility}, turns_to_solve: {self.turns_to_solve}"

    def normalize(self, scores):
        """
        Using potion scores from all available potions, compute the normalized rating
        :param [PotionScore] scores: All available potion scores
        """
        self.normalized_cost = -self._normalize_attribute("cost", scores)
        self.normalized_distance = -self._normalize_attribute("distance", scores)
        self.normalized_points_per_cost = self._normalize_attribute(
            "points_per_cost", scores
        )
        self.normalized_spell_compatibility = self._normalize_attribute(
            "spell_compatibility", scores
        )
        self.normalized_turns_to_solve = -self._normalize_attribute(
            "turns_to_solve", scores
        )
        normalized_total = self._apply_weights(POTION_WEIGHTS)
        self.normalized_score = normalized_total

    # ----------------------------------------
    # Private
    # ----------------------------------------
    def _compute_spell_compatibility(self, witch):
        score = 0
        for i, color in enumerate(COLORS):
            witch_generation = getattr(witch.generation_delta, color)
            potion_color_value = getattr(self.potion.delta, color)
            score -= witch_generation * potion_color_value
            # score -= witch_generation * potion_color_value * RESOURCE_VALUES[color]
        return score

    def _compute_turns_to_solve(self):
        return self.potion.p1_turns


class SpellScore(Score):
    """
    Score representation of a Spell to rank it amongst other spells, based on:
        How much money it brings
        Can we cast it NOW
        How hard it is to cast
        Can it be repeated
    """

    def __init__(self, spell):
        """
        Instantiates the score of a Spell
        :param spell: The spell to score
        :type spell: GrimoireSpell or Spell
        """
        self.spell = spell
        # Ranking factors
        self.benefits = self._convert_delta_to_money(self.spell.delta)
        self.blue_earnings = self.spell.blue_earnings
        self.blue_tax = self.spell.blue_tax
        self.difficulty = self._compute_difficulty(ME, self.spell.delta)
        self.repeatable = self.spell.repeatable

    def __repr__(self):
        return (
            f"SpellScore("
            f"score: {self.normalized_score}, "
            f"benefits: {self.benefits}, "
            f"blue_earnings: {self.blue_earnings}, "
            f"blue_tax: {self.blue_tax}, "
            f"difficulty: {self.difficulty}, "
            f"repeatable: {self.repeatable})"
        )

    def normalize(self, scores):
        """
        Using spell scores from all available spells, compute the normalized rating
        :param [SpellScore] scores: All available spell scores
        """
        self.normalized_benefits = self._normalize_attribute("benefits", scores)
        self.normalized_blue_earnings = self._normalize_attribute(
            "blue_earnings", scores
        )
        self.normalized_blue_tax = -self._normalize_attribute("blue_tax", scores)
        self.normalized_difficulty = -self._normalize_attribute("difficulty", scores)
        self.normalized_repeatable = int(self.repeatable)
        self.normalized_score = self._apply_weights(SPELL_WEIGHTS)


# --------------------------------------------------------------------------------
# Utility
# --------------------------------------------------------------------------------
def get_spell_for_resource(container, resource):
    """
    Searches and returns a spell that can yield the requested resource
    :param dict container: The dict of spells to search in
    :param str resource: Name/color of the target resource
    :return: The spell that yields the request resource
    :rtype: None or Spell
    """
    eligible_spells = [
        spell for spell in container.values() if getattr(spell.delta, resource) > 0
    ]
    eligible_spells.sort(key=lambda x: getattr(x.delta, resource), reverse=True)
    if len(eligible_spells) > 0:
        return eligible_spells[0]
    return None


def rank_potions():
    """Computes all potion scores and then perform the score normalization"""
    # Scoring
    scores = []
    for potion in POTIONS.values():
        potion.compute_score()
        scores.append(potion.score)
    for score in scores:
        score.normalize(scores)
    # Ranking
    RANKED_POTIONS.clear()
    potions = list(POTIONS.values())
    potions.sort(key=lambda x: x.score.normalized_score, reverse=True)
    for potion in potions:
        RANKED_POTIONS.append(potion)


def rank_spells():
    # Scoring
    scores = []
    for spell in SPELLS.values():
        spell.compute_score()
        scores.append(spell.score)
    for spell in GRIMOIRE_SPELLS.values():
        spell.compute_score()
        scores.append(spell.score)
    for score in scores:
        score.normalize(scores)
    # Ranking
    SPELL_RANKINGS.clear()
    spells = list(SPELLS.values()) + list(GRIMOIRE_SPELLS.values())
    spells.sort(key=lambda x: x.score.normalized_score, reverse=True)
    for spell in spells:
        SPELL_RANKINGS.append(spell)


def remove_missing_actions():
    """Unlists all actions that have been removed from the game"""
    for container in [POTIONS, SPELLS, OPPONENT_SPELLS, GRIMOIRE_SPELLS]:
        ids_to_remove = [
            action_id for action_id in container if action_id not in TURN_ACTIONS
        ]
        for action_id in ids_to_remove:
            del container[action_id]


def debug(*message):
    """
    Debug printing for Codingame.com
    :param message: Elements to print
    """
    print(*message, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------------
# Storage
# --------------------------------------------------------------------------------
global TIMER

# Items
POTIONS = {}
SPELLS = {}
OPPONENT_SPELLS = {}
GRIMOIRE_SPELLS = {}

# Players
WITCHES = []
ME = None
OPPONENT = None

# Scoring
RANKED_POTIONS = []
SPELL_RANKINGS = []

# --------------------------------------------------------------------------------
# Game loop
# --------------------------------------------------------------------------------
TIMER = TurnTimer()
first_turn = True
while True:
    TIMER.reset()

    # Register or update actions
    TURN_ACTIONS = {}
    action_count = int(input())
    for i in range(action_count):
        action_info = input().split()
        action = Action(action_info)
        action.register()  # Will create or update
        TURN_ACTIONS[action.id] = action
    remove_missing_actions()

    # Players information
    if first_turn:
        for i in range(2):
            witch_info = [int(j) for j in input().split()]
            witch = Witch(witch_info, i == 0)
            WITCHES.append(witch)
        ME = WITCHES[0]
        OPPONENT = WITCHES[1]
        first_turn = False
    else:
        for i in range(2):
            witch_info = [int(j) for j in input().split()]
            witch = WITCHES[i]
            witch.update(witch_info)

    # Computations
    rank_spells()
    rank_potions()

    for potion in RANKED_POTIONS:
        debug(potion.id, potion.score)

    for spell in SPELL_RANKINGS:
        debug(spell.id, spell.is_grimoire, spell.score)

    ME.play()

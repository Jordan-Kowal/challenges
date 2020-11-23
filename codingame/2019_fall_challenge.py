# ------------------------------------------------------------
# PATCH NOTES
# ------------------------------------------------------------
# The changes in this version are as follows:
#   * New grid
#   * Don't use trap
#   ! If digging on potential trap, nobody must be around this trap
#   ! When moving, avoid having 2 robots nearby the same trap
#   ! (Try to add the "and an enemy is nearby")
#   ! Avoid "spwan mine wall" by having only one person at the base after turn X ?


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
import math
import sys


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------
RADAR_SETUPS = {
    1: [
        (5, 0),  # 0 will be replaced by robot.y
        (10, 3),
        (10, 11),
        (15, 7),
        (20, 3),
        (20, 11),
        (25, 7),
        (28, 3),
        (28, 11),
        (3, 2),
        (3, 12),
        (14, 1),
        (14, 13),
    ],
}
X_SETUPS = {
    1: 4,
}
SETUP = 1
HARDCODED_RADARS = RADAR_SETUPS[SETUP]
FIRST_X = X_SETUPS[SETUP]
GET_TRAP_MIN_TURN = 0
GET_TRAP_MAX_TURN = 0
DIG_ENEMY_TRAP_MIN_TURN = 100
LOW_ORE = 10
COMMENTS = True


# ------------------------------------------------------------
# INITAL DATA
# ------------------------------------------------------------
# Game
WIDTH, HEIGHT = [int(i) for i in input().split()]

# Robots
ALL_ROBOTS = {}
MY_ROBOTS = []
ENEMY_ROBOTS = []

# Items
COOLDOWNS = {
    "RADAR": 0,
    "TRAP": 0
}
ITEM_NAMES = {
    -1: None,
    2: "RADAR",
    3: "TRAP",
    4: "ORE",
}

# Game
MY_SCORE = 0
ENEMY_SCORE = 0
TURN = 0

# Ore
CELLS_SCANNED = set()
CELLS_WITH_ORE = set()
# Holes
CELLS_WITHOUT_HOLE = set()
MY_HOLES = set()
ENEMY_HOLES = set()
NEW_HOLES = set()
# Traps
MY_TRAPS = set()
INCOMING_TRAPS = set()
ENEMY_TRAPS = set()


# ------------------------------------------------------------
# CLASS
# ------------------------------------------------------------
class Robot:
    # --------------------
    # Constants
    # --------------------
    ACTIONS = [
        ("play_dead", []),
        ("first_turn_action", []),
        ("trigger_trap", []),
        ("go_to_destination", []),
        ("bring_back_ore", []),
        ("pick_up_item", []),
        ("move_to_hardcoded_radar", []),
        ("burry_hardcoded_radar", []),
        ("dig_adjacent_ore", [True, 0]),
        ("move_to_ore", [True, 0]),
        ("go_get_radar", []),
        ("dig_adjacent_ore", [False, DIG_ENEMY_TRAP_MIN_TURN]),
        ("move_to_ore", [False, DIG_ENEMY_TRAP_MIN_TURN]),
        ("dig_unknown_cell", []),
        ("move_to_unknown_cell", []),
        ("wait_it_out", []),
    ]
    GETTING_RADAR = False

    # --------------------
    # Core Methods
    # --------------------
    def __init__(self, id, type, cell):
        """Initializes our robot and its attributes"""
        # General
        self.dead = False
        self.id = id
        self.type = type
        self.last_action = None
        self.index = id if id < 5 else id - 5
        # Dig setup
        self.last_dig_cell = None
        self.dig_objective = None
        # Mouvement setup
        self.position = cell
        self.previous_position = cell
        self.destination = None
        # Item setup
        self.item = None
        self.get_first_radar = False
        self.getting_radar = False
        self.hardcoded_radar_cell = None

    # --------------------
    # Game Actions
    # --------------------
    def dig(self, cell, comment=""):
        """Gives the "DIG" order. The robot will dig on the given cell (x, y)"""
        self.real_time_dig_update(cell)
        self.last_dig_cell = cell
        self.dig_objective = None
        self.last_action = "DIG"
        if not COMMENTS:
            comment = ""
        print("DIG", *cell, comment)

    def move(self, cell, closest=True, comment=""):
        """Gives the "MOVE" order. The robot will move towards the given cell (x, y)"""
        if closest:
            self.dig_objective = cell
            cell = self.get_closest_unoccupied_cell(self.position, cell)
        self.destination = cell
        self.last_action = "MOVE"
        comment += " " + str(self.dig_objective)
        if not COMMENTS:
            comment = ""
        print("MOVE", *cell, comment)

    def request(self, item, comment=""):
        """Gives the "REQUEST" order. The robots asks for a RADAR or a TRAP"""
        COOLDOWNS[item] = 5
        self.item = item
        self.last_action = "REQUEST"
        if not COMMENTS:
            comment = ""
        print("REQUEST", item, comment)

    def wait(self, comment=""):
        """Gives the "WAIT" order. The robot does nothing"""
        self.last_action = "WAIT"
        if not COMMENTS:
            comment = ""
        print("WAIT", comment)

    # --------------------
    # ACTION CHOICES
    # --------------------
    def play(self):
        for function_name, args in self.ACTIONS:
            function = getattr(self, function_name)
            if len(args) > 0:
                done = function(*args)
            else:
                done = function()
            if done:
                break

    def play_dead(self):
        if self.dead:
            self.wait("play dead")
            return True

    def first_turn_action(self):
        if TURN == 1:
            if self.get_first_radar:
                self.request("RADAR", "first turn action")
            else:
                cell = (FIRST_X, self.y)
                self.move(cell, False, "first turn action")
            return True

    def trigger_trap(self):
        adjacent_cells = get_adjacent_cells(self.position)
        for cell in adjacent_cells:
            if cell in MY_TRAPS:
                friendly_robots = len(adjacent_robots(cell, 0))
                enemy_robots = len(adjacent_robots(cell, 1))
                if friendly_robots < enemy_robots:
                    self.dig(cell, "trigger trap")
                    return True

    def go_to_destination(self):
        if self.destination is not None:
            self.move(self.destination, False, "go to destination")
            return True

    def bring_back_ore(self):
        if self.item == "ORE":
            cell = (0, self.y)
            self.move(cell, False, "bring back ore")
            return True

    def pick_up_item(self):
        if self.item is None and self.x == 0:
            if not COOLDOWNS["RADAR"] and calculate_safe_ore() < LOW_ORE:
                Robot.GETTING_RADAR = False
                self.getting_radar = False
                self.request("RADAR", "pick up item")
                return True
            elif not COOLDOWNS["TRAP"]:
                if TURN >= GET_TRAP_MIN_TURN and TURN <= GET_TRAP_MAX_TURN and not most_alive_robots():
                    self.request("TRAP", "pick up item")
                    return True

    def move_to_hardcoded_radar(self):
        if self.item == "RADAR" and self.destination is None and self.x == 0:
            if len(HARDCODED_RADARS) > 0:
                cell = self.choose_which_hardcoded_radar()
                if self.get_first_radar:
                    self.get_first_radar = False
                    cell = (cell[0], self.y)
                self.hardcoded_radar_cell = cell
                self.move(cell, True, "move to hardcoded radar")
                return True

    def burry_hardcoded_radar(self):
        if self.hardcoded_radar_cell is not None and self.destination is None:
            radar_cell = self.hardcoded_radar_cell
            self.hardcoded_radar_cell = None
            if radar_cell in MY_TRAPS.union(ENEMY_TRAPS):
                cells = get_adjacent_cells(self.position)
                for cell in cells:
                    if cell not in MY_TRAPS.union(ENEMY_TRAPS):
                        radar_cell = cell
                        break
                else:
                    radar_cell = None
            if radar_cell is not None:
                self.dig(radar_cell, "burry hardcoded radar")
                return True

    def dig_adjacent_ore(self, avoid_enemy_traps=True, min_turn=0):
        if TURN > min_turn:
            alive_robots = [robot for robot in MY_ROBOTS if not robot.dead]
            if avoid_enemy_traps or len(alive_robots) > 2:
                traps = get_traps(avoid_enemy_traps)
                adjacent_cells = get_adjacent_cells(self.position)
                for cell in adjacent_cells:
                    if cell not in traps and cell in CELLS_WITH_ORE:
                        self.dig(cell, "dig adjacent ore ({})".format(avoid_enemy_traps))
                        return True

    def move_to_ore(self, avoid_enemy_traps=True, min_turn=0):
        if TURN > min_turn:
            alive_robots = [robot for robot in MY_ROBOTS if not robot.dead]
            if avoid_enemy_traps or len(alive_robots) > 2:
                traps = get_traps(avoid_enemy_traps)
                sorted_cells = sort_cells_closest(self.position, CELLS_WITH_ORE)
                sorted_cells = list(filter(lambda x: x not in traps, sorted_cells))
                for cell in sorted_cells:
                    robot_amount = len(friendly_robots_working_this_cell(cell))
                    ore = MAP_DATA[cell]["ore"]
                    if avoid_enemy_traps or robot_amount == 0:
                        if robot_amount < ore:
                            self.move(cell, True, "move to ore ({})".format(avoid_enemy_traps))
                            return True

    def go_get_radar(self):
        if len(HARDCODED_RADARS) > 0 and not Robot.GETTING_RADAR:
            turn_to_base = math.ceil(self.x / 4)
            if turn_to_base > COOLDOWNS["RADAR"]:
                Robot.GETTING_RADAR = True
                self.getting_radar = True
                cell = (0, self.y)
                self.move(cell, False, "go get radar")
                return True

    def dig_unknown_cell(self):
        adjacent_cells = get_adjacent_cells(self.position)
        for cell in adjacent_cells:
            if not MAP_DATA[cell]["hole"] and cell not in CELLS_SCANNED and cell[0] > 0:
                self.dig(cell, "dig unknown cell")
                return True

    def move_to_unknown_cell(self):
        unknown_cells = CELLS_WITHOUT_HOLE.difference(CELLS_SCANNED)
        if len(unknown_cells) > 0:
            sorted_cells = sort_cells_closest(self.position, unknown_cells)
            for cell in sorted_cells:
                if cell[0] > 0:
                    self.move(cell, True, "move to unknown cell")
                    return True

    def wait_it_out(self):
        self.wait("wait it out")
        return True

    # --------------------
    # Helper Methods
    # --------------------
    def choose_which_hardcoded_radar(self):
        """
        Description:
            Find the next closest hardcoded radar for your robot
            The hardcoded radar is then removed from the list
            Two radars are compared only when on the same column
        Returns:
            tuple: Coordinates (x, y) of the hardcoded radar
        """
        found = False
        if len(HARDCODED_RADARS) > 1:
            x1, x2 = HARDCODED_RADARS[0][0], HARDCODED_RADARS[1][0]
            if x1 == x2:
                y1, y2 = HARDCODED_RADARS[0][1], HARDCODED_RADARS[1][1]
                diff_y1, diff_y2 = abs(self.y - y1), abs(self.y - y2)
                if diff_y2 < diff_y1:
                    cell = HARDCODED_RADARS.pop(1)
                    found = True
        if not found:
            cell = HARDCODED_RADARS.pop(0)
        return cell

    def get_closest_unoccupied_cell(self, start_cell, end_cell):
        """
        Description:
            Returns the closest adjacent cell of a "end_cell" relatively to a "start_cell"
        Args:
            start_cell (tuple): Coordinates (x, y) of the starting point
            end_cell (tuple): Coordinates (x, y) of the ending point
        Returns:
            tuple: Coordinates (x, y) of the closest adjacent cell
        """
        cells = get_adjacent_cells(end_cell)
        sorted_cell = sort_cells_closest(start_cell, cells)
        robots = [MY_ROBOTS[i] for i in range(self.index)]
        for cell in sorted_cell:
            occupied = False
            for robot in robots:
                if robot.position == cell:
                    occupied = True
                    break
            if not occupied:
                return cell

    def guess_enemy_pickup_trap(self):
        """Guesses if an enemy has picked up a trap"""
        if self.immobile and self.x == 0:
            self.item = "TRAP"

    def guess_enemy_potential_traps(self):
        """Guesses if a trap has been burried by an enemy"""
        if self.immobile and self.x > 0 and self.item == "TRAP":
            adjacent_cells = get_adjacent_cells(self.position)
            # He made a new hole, 100% sure
            for cell in adjacent_cells:
                if cell in NEW_HOLES.intersection(ENEMY_HOLES):
                    robot_count = len(adjacent_robots(cell, 1))
                    if robot_count == 1:
                        self.item = None
                        self.last_dig_cell = cell
                        ENEMY_TRAPS.add(cell)
                        return
            # If already existing holes, assume they have traps
            for cell in adjacent_cells:
                if cell in MY_HOLES.union(ENEMY_HOLES):
                    self.item = None
                    ENEMY_TRAPS.add(cell)

    def just_died(self):
        """Checks if a robot just died this turn"""
        if self.position == (-1, -1) and self.previous_position != self.position:
            self.dead = True
            self.dig_objective = None
            if self.getting_radar:
                Robot.GETTING_RADAR = False
                self.getting_radar = False
            return True
        return False

    def real_time_dig_update(self, cell):
        """
        Description:
            Update the MAP_DATA and our "cell sets" in realtime for better decision making
            That way, our robots don't have to way until next turn to get updated data
        Args:
            cell (tuple): Coordinates (x, y) of the cell
        """
        # Update the "hole" info
        MAP_DATA[cell]["hole"] = True
        MY_HOLES.add(cell)
        if cell in CELLS_WITHOUT_HOLE:
            CELLS_WITHOUT_HOLE.remove(cell)
        # Update the item drop
        if self.item == "TRAP":
            MY_TRAPS.add(cell)
        self.item = None
        # Update the ore
        ore = MAP_DATA[cell]["ore"]
        if ore not in {"?", 0}:
            ore -= 1
            self.item = "ORE"
            if ore == 0:
                CELLS_WITH_ORE.remove(cell)
            MAP_DATA[cell]["ore"] = ore

    def turn_update(self, cell, item):
        """
        Description:
            Handles the turnly update of a robot information
            Methods used are different based on robot's type
        Args:
            cell (tuple): Coordinates (x, y) of the cell
            item (int): The currently carried item (represented by a number)
        """
        self.position = cell
        if self.position == (-1, -1):
            self.dead = True
        if self.type == 0:
            self.turn_update_friendly(cell, item)
        elif self.type == 1:
            self.turn_update_enemy(cell)
        self.previous_position = cell

    def turn_update_enemy(self, cell):
        """
        Description:
            Updates an ENEMY robot information at the beginning of a turn
            Since we only know its position, we can only assume actions based on movement
        Args:
            cell (tuple): Coordinates (x, y) of the cell
        """
        if not self.dead:
            self.guess_enemy_pickup_trap()
            self.guess_enemy_potential_traps()

    def turn_update_friendly(self, cell, item):
        """
        Description:
            Updates a FRIENDLY robot information at the beginning of a turn
        Args:
            cell (tuple): Coordinates (x, y) of the cell
            item (int): The currently carried item (represented by a number)
        """
        # Item
        item = ITEM_NAMES[item]
        self.item = item
        # Updating cell ore info
        if self.last_action == "DIG" and self.item is None:
            if self.last_dig_cell in CELLS_WITH_ORE:
                CELLS_WITH_ORE.remove(self.last_dig_cell)
        if self.just_died():
            if self.last_action == "DIG":
                remove_traps_recursively(self.last_dig_cell)
        if self.destination == cell:
            self.destination = None
        self.previous_position = cell
        # Map data
        if min(cell) >= 0:
            if self.type == 0:
                MAP_DATA[cell]["robots"]["ME"] += 1
            else:
                MAP_DATA[cell]["robots"]["ENEMY"] += 1

    # --------------------
    # Custom Properties
    # --------------------
    @property
    def immobile(self):
        """Dynamic property that indicates if the robot has moved"""
        return self.position == self.previous_position

    @property
    def x(self):
        """Dynamic property that returns the robot's X coordinate"""
        return self.position[0]

    @property
    def y(self):
        """Dynamic property that returns the robot's Y coordinate"""
        return self.position[1]


# ------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------
def adjacent_robots(cell, type):
    """
    Description:
        Returns the list of robots that are adjacent to the given cell
        You can choose between friendly and enemy by using "type"
    Args:
        cell (tuple): Coordinates (x, y) of a cell
    Returns:
        list: List of robots on adjacent cells
    """
    cells = get_adjacent_cells(cell)
    all_robots = MY_ROBOTS + ENEMY_ROBOTS
    robots = [robot for robot in all_robots if robot.type == type]
    found_robots = []
    for robot in robots:
        if robot.position in cells:
            found_robots.append(robot)
    return found_robots


def calculate_safe_ore():
    """
    Description:
        Calculates the amount of SAFE ore available on the map
    Returns:
        int: Amount of ore available
    """
    amount = 0
    for cell, data in MAP_DATA.items():
        if cell not in MY_TRAPS.union(ENEMY_TRAPS):
            if data["ore"] not in {"?", 0}:
                amount += data["ore"]
    return amount


def choose_robot_for_first_radar():
    """
    Description:
        Finds and returns the robot that is the closest to the center of the map
    Returns:
        Robot: The closest friendly robot relative to the center
    """
    robots = MY_ROBOTS.copy()
    center = int(HEIGHT/2)
    center_diff = [abs(robot.position[1] - center) for robot in robots]
    index = center_diff.index(min(center_diff))
    closest_robot = robots[index]
    return closest_robot


def create_robot(id, type, cell):
    """
    Description:
        Creates a robot and puts it in our correct datasets
    Args:
        id (int): Unique ID of the entity
        type (int): 0 for our robot, 1 for an enemy robot
        cell (tuple): Coordinates (x, y) of the cell
    """
    robot = Robot(id, type, cell)
    ALL_ROBOTS[id] = robot
    if type == 0:
        MY_ROBOTS.append(robot)
    else:
        ENEMY_ROBOTS.append(robot)


def friendly_robots_working_this_cell(cell):
    """
    Description:
        Returns the list of friendly robots currently working on this cell
    Args:
        cell (tuple): Coordinates (x, y) of the cell
    Returns:
        list: List of the eligible robots
    """
    robots = [robot for robot in MY_ROBOTS if robot.dig_objective == cell]
    return robots


def generate_map_data(width, height):
    """
    Description:
        Generates the map_data at the begining of the game
        Keys are coordinates (x, y) and they contain data regarding the cell
    Args:
        width (int): Width of the grid, given by the game
        height (int): Height of the grid, given by the game
    Returns:
        dict: Dict with coordinates (x, y) as keys, and dicts as values
    """
    map_data = {}
    for i in range(width):
        for j in range(height):
            CELLS_WITHOUT_HOLE.add((i, j))
            map_data[(i, j)] = {
                "robots": {
                    "ME": 0,
                    "ENEMY": 0,
                },
                "hole": False,
                "ore": "?",
            }
    return map_data


def get_adjacent_cells(cell):
    """
    Description:
        Finds and returns the adjacent cells of a given cell (including the original cell)
        The result is a SET containing between 3 to 5 elements
    Args:
        cell (tuple): Coordinates (x, y) of the cell
    Returns:
        set: Set of 3 to 5 coordinates (x, y)
    """
    x, y = cell
    cells = set((
        (x-1, y),
        (x+1, y),
        (x, y),
        (x, y-1),
        (x, y+1),
    ))
    cells = set(filter(is_cell_in_grid, cells))
    return cells


def get_traps(all_traps=True):
    """
    Description:
        Returns a set containing all the cells that have traps
        Can be set to check either ALL traps or only OURS
    Args:
        all_traps (bool, optional): Determines if we get ALL traps. Defaults to True.
    Returns:
        set: Set of tuples which are cell coordinates
    """
    if all_traps:
        traps = MY_TRAPS.union(ENEMY_TRAPS)
    else:
        traps = MY_TRAPS
    return traps


def is_cell_in_grid(cell):
    """
    Description:
        Checks if a given cell is within the limit of the grid
    Args:
        cell (tuple): Coordinates (x, y) of the cell
    Returns:
        bool: True if the cell is within WIDTH/HEIGHT
    """
    x, y = cell
    if x in range(WIDTH) and y in range(HEIGHT):
        return True
    return False


def most_alive_robots():
    """
    Description:
        Checks if we have more robots alive than our enemy
    Returns:
        bool: True if we have strickly more robots
    """
    my_robots = [robot for robot in MY_ROBOTS if not robot.dead]
    enemy_robots = [robot for robot in ENEMY_ROBOTS if not robot.dead]
    if len(my_robots) > len(enemy_robots):
        return True
    return False


def remove_my_triggered_traps():
    """Removes our missing trap from our info sets"""
    removed_traps = MY_TRAPS.difference(MY_TRAPS_THIS_TURN)
    for cell in removed_traps:
        remove_traps_recursively(cell)


def remove_traps_recursively(initial_cell, first=True):
    """
    Description:
        Remove traps recursively by declaring which cell triggered the first trap
        We spread the reaction only on our traps, since enemy traps are only guessed
    Args:
        initial_cell (tuple): Coordinates (x, y) of a triggered trap
    """
    if initial_cell in MY_TRAPS:
        MY_TRAPS.remove(initial_cell)
        adjacent_cells = get_adjacent_cells(initial_cell)
        for cell in adjacent_cells:
            remove_traps_recursively(cell, False)
    elif initial_cell in ENEMY_TRAPS and first:
        ENEMY_TRAPS.remove(initial_cell)
        adjacent_cells = get_adjacent_cells(initial_cell)
        for cell in adjacent_cells:
            if cell in MY_TRAPS:
                remove_traps_recursively(cell, False)
    # for traps in [MY_TRAPS, ENEMY_TRAPS]:
    #     if initial_cell in traps:
    #         traps.remove(initial_cell)
    #         adjancent_cells = get_adjacent_cells(initial_cell)
    #         for cell in adjancent_cells:
    #             remove_traps_recursively(cell)


def sort_cells_closest(start_cell, cells):
    """
    Description:
        Returns a sorted list of cells by 'closest' based on the given start cell
    Args:
        start_cell (tuple): Coordinates (x, y) of the reference cell
        cells (list): List of (x, y) tuples that are the cells to compare
    Returns:
        list: A list containing all the "cells", sorted by closeness relative to "start_cell"
    """
    sorted_list = sorted(cells, key=lambda cell: abs(cell[0]-start_cell[0]) + abs(cell[1] - start_cell[1]))
    return sorted_list


def turn_cell_update(cell, ore, hole):
    """
    Description:
        Updates the MAP_DATA and our "cell sets" with ore and hole info
        The game will send us this data for every cell, at the start of every turn
    Args:
        cell (tuple): Coordinates (x, y) of the cell
        ore (str): String that can either be "?" or a number
        hole (int): 0 if no hole has been dug, 1 otherwise
    """
    # Ore update
    if ore != "?":
        ore = int(ore)
        MAP_DATA[cell]["ore"] = ore
        CELLS_SCANNED.add(cell)
        if ore > 0:
            CELLS_WITH_ORE.add(cell)
        elif cell in CELLS_WITH_ORE:
            CELLS_WITH_ORE.remove(cell)
    else:
        existing_ore_data = MAP_DATA[cell]["ore"]
        if not isinstance(existing_ore_data, int):
            MAP_DATA[cell]["ore"] = ore
    # Hole update
    if hole:
        if cell not in MY_HOLES.union(ENEMY_HOLES):
            NEW_HOLES.add(cell)
        if cell not in MY_HOLES:
            ENEMY_HOLES.add(cell)
        if cell in CELLS_WITHOUT_HOLE:
            CELLS_WITHOUT_HOLE.remove(cell)
    MAP_DATA[cell]["hole"] = bool(hole)
    # Robot count reset
    MAP_DATA[cell]["robots"]["ME"] = 0
    MAP_DATA[cell]["robots"]["ENEMY"] = 0


def turn_entity_update(id, type, cell, item):
    """
    Description:
        Updates either a robot or our dataset, based on the given information
        This function is called at the start of each turn, for each identified entity
    Args:
        id (int): Unique ID of the entity
        type (int): Number from 0 to 3 with (0: our robot, 1: enemy robot, 2: radar, 3: emp)
        cell (tuple): Coordinates (x, y) of the cell
        item (int): The currently carried item (represented by a number)
    """
    if id in ALL_ROBOTS.keys():
        robot = ALL_ROBOTS[id]
        robot.turn_update(cell, item)
    else:
        if type == 2:
            pass
        if type == 3:
            MY_TRAPS.add(cell)
            MY_TRAPS_THIS_TURN.add(cell)


# ------------------------------------------------------------
# GAME LOOP
# ------------------------------------------------------------
MAP_DATA = generate_map_data(WIDTH, HEIGHT)
while True:
    # Score update
    NEW_HOLES = set()
    MY_TRAPS_THIS_TURN = set()
    MY_SCORE, ENEMY_SCORE = [int(i) for i in input().split()]
    TURN += 1

    # Ore and hole update
    for i in range(HEIGHT):
        inputs = input().split()
        for j in range(WIDTH):
            cell = (j, i)
            ore = inputs[2*j]
            hole = int(inputs[2*j+1])
            turn_cell_update(cell, ore, hole)

    # Item update
    entity_count, COOLDOWNS["RADAR"], COOLDOWNS["TRAP"] = [int(i) for i in input().split()]

    # Entity update
    for i in range(entity_count):
        id, type, x, y, item = [int(j) for j in input().split()]
        cell = (x, y)
        if TURN == 1:
            create_robot(id, type, cell)
        else:
            turn_entity_update(id, type, cell, item)
    remove_my_triggered_traps()

    # First turn action setup
    if TURN == 1:
        closest_robot = choose_robot_for_first_radar()
        closest_robot.get_first_radar = True

    # Action
    for i in range(5):
        robot = MY_ROBOTS[i]
        robot.play()

# Built-in
import sys
from typing import Dict, List, Optional, Set, Tuple

# --------------------------------------------------
# Types
# --------------------------------------------------
Area = Tuple[int, int, int, int]
Position = Tuple[int, int]

# --------------------------------------------------
# Constants
# --------------------------------------------------
LIGHT_MAX_DISTANCE = 2_000
LIGHT_MIN_DISTANCE = 800
LIGHT_BATTERY_COST = 5
VALUE_BY_TYPE: Dict[int, int] = {0: 1, 1: 2, 2: 3}
DEPTHS_BY_TYPE: Dict[int, Tuple[int, int]] = {
    0: (2_500, 5_000),
    1: (5_000, 7_500),
    2: (7_500, 1_0000),
}
GRID_WIDTH = 10_000


# --------------------------------------------------
# Classes
# --------------------------------------------------
class Player:
    def __init__(self, is_me: bool) -> None:
        self.is_me = is_me
        self.score: int = 0
        self.save_count: int = 0
        self.saved_creature_ids: Set[int] = set()
        self.drones: Dict[int, Drone] = {}
        self.ordered_drone_ids: List[int] = []

    def __str__(self) -> str:
        return "Me" if self.is_me else "Foe"

    def __repr__(self) -> str:
        return str(self)

    @property
    def saved_creatures(self) -> Set["Creature"]:
        return {CREATURES_BY_ID[i] for i in self.saved_creature_ids}

    @property
    def scanned_or_saved_creature_ids(self) -> Set[int]:
        ids = self.saved_creature_ids
        for drone in self.drones.values():
            ids |= drone.scanned_creature_ids
        return ids

    @property
    def scanned_or_saved_creatures(self) -> Set["Creature"]:
        return {CREATURES_BY_ID[i] for i in self.scanned_or_saved_creature_ids}

    def update_score_from_input(self) -> None:
        self.score = int(input())

    def update_save_count_from_input(self) -> None:
        self.save_count = int(input())
        self.saved_creature_ids = {int(input()) for _ in range(self.save_count)}

    def update_drones_vitals_from_input(self) -> None:
        my_drone_count = int(input())
        order = []
        for _ in range(my_drone_count):
            drone_id, *data = [int(j) for j in input().split()]
            drone = self.drones.get(drone_id) or Drone(self, drone_id)
            drone.update_vitals(*data)
            self.drones[drone_id] = drone
            order.append(drone_id)
        self.ordered_drone_ids = order


class Drone:
    def __init__(self, player: Player, _id: int) -> None:
        self.player = player
        self.id = _id
        self.x: int = 0
        self.y: int = 0
        self.emergency: int = 0
        self.battery: int = 0
        self.scanned_creature_ids: Set[int] = set()
        self.last_turn_scanned_creature_ids: Set[int] = set()
        self.last_turn_light: bool = False

    def __str__(self) -> str:
        return f"Drone {self.id} ({self.position}) for {self.player}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def position(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def visible_area(self) -> Area:
        amount = int(LIGHT_MIN_DISTANCE * LIGHT_SQUARE_RATIO)
        if self.last_turn_light:
            amount = int(LIGHT_MAX_DISTANCE * LIGHT_SQUARE_RATIO)
        area = self.x, self.y, self.x, self.y
        return increase_area(area, amount)

    @property
    def best_creature_with_distance(self) -> Tuple["Creature", int]:
        creature_data: List[Tuple[Creature, int, float]] = []
        for creature in CREATURES_BY_ID.values():
            distance, score = creature.compute_score_for_drone(self)
            creature_data.append((creature, distance, score))
        creature_data.sort(key=lambda x: x[2])
        for creature, distance, score in creature_data:
            debug(f"{creature} has score {score} and distance {distance}")
        best_creature, distance, _ = creature_data[-1]
        return best_creature, distance

    def play_turn(self) -> None:
        creature, distance = self.best_creature_with_distance
        x, y = creature.next_position
        activate_light = int(
            LIGHT_MAX_DISTANCE > distance > LIGHT_MIN_DISTANCE
            and self.battery > LIGHT_BATTERY_COST
        )
        self.move(x, y, activate_light)

    def update_vitals(self, x: int, y: int, emergency: int, battery: int) -> None:
        self.x = x
        self.y = y
        self.emergency = emergency
        # Battery
        self.last_turn_light = self.battery > battery
        self.battery = battery

    def update_scans(self, scanned_ids: Set[int]) -> None:
        if len(scanned_ids) > len(self.scanned_creature_ids):
            self.last_turn_scanned_creature_ids = (
                scanned_ids - self.scanned_creature_ids
            )
        else:
            self.last_turn_scanned_creature_ids = set()
        self.scanned_creature_ids = scanned_ids

    @staticmethod
    def move(x: int, y: int, light: int) -> None:
        print(f"MOVE {x} {y} {light}")

    @staticmethod
    def wait(light: int) -> None:
        print(f"WAIT {light}")


class Creature:
    def __init__(self, _id: int, color: int, _type: int) -> None:
        # Fixed info
        self.id = _id
        self.color = color
        self.type = _type
        self.value: int = VALUE_BY_TYPE[_type]
        # Available area
        self.width_min, self.width_max = 0, GRID_WIDTH
        self.depth_min, self.depth_max = DEPTHS_BY_TYPE[_type]
        # Position
        self.x: int = 0
        self.y: int = 0
        self.vx: int = 0
        self.vy: int = 0
        self.is_visible: bool = False
        self.last_visible_turn: Optional[int] = None
        # Grid
        self.x_min, self.x_max = 0, GRID_WIDTH
        self.y_min, self.y_max = DEPTHS_BY_TYPE[_type]
        # Radar
        self.last_turn_radar_info: Dict[int, str] = {}
        self.radar_info: Dict[int, str] = {}

    def __str__(self) -> str:
        return f"Creature {self.id} ({self.position})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def position(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def next_position(self) -> Tuple[int, int]:
        return self.x + self.vx, self.y + self.vy

    @property
    def max_area(self) -> Area:
        return self.width_min, self.depth_min, self.width_max, self.depth_max

    @property
    def area(self) -> Area:
        return self.x_min, self.y_min, self.x_max, self.y_max

    @property
    def radar_info_has_changed(self) -> bool:
        if not self.last_turn_radar_info:
            return False
        for drone_id, radar in self.radar_info.items():
            if radar != self.last_turn_radar_info.get(drone_id):
                return True
        return False

    @property
    def foe_drones_that_scanned_it_last_turn(self) -> List[Drone]:
        return [
            drone
            for drone in FOE.drones.values()
            if self.id in drone.last_turn_scanned_creature_ids
        ]

    def compute_position_for_turn(self) -> None:
        if self.is_visible:
            return
        # Update width range based on radar info
        for drone_id, radar in self.radar_info.items():
            drone = ME.drones[drone_id]
            if "L" in radar and drone.x < GRID_WIDTH // 2:
                self.width_min, self.width_max = 0, GRID_WIDTH // 2
            elif "R" in radar and drone.x >= GRID_WIDTH // 2:
                self.width_min, self.width_max = GRID_WIDTH // 2, GRID_WIDTH
        # Compute area from previous but within bounds
        area = increase_area(self.area, CREATURE_MOVE_SPEED)
        area = compute_area_overlap(area, self.max_area)
        # If scanned last turn, narrow area
        for drone in self.foe_drones_that_scanned_it_last_turn:
            area = compute_area_overlap(drone.visible_area, area)
        # Use radar info to narrow area
        for drone_id, radar in self.radar_info.items():
            drone = ME.drones[drone_id]
            areas = {
                "TL": (self.width_min, self.depth_min, drone.x, drone.y),
                "TR": (drone.x, self.depth_min, self.width_max, drone.y),
                "BL": (self.width_min, drone.y, drone.x, self.depth_max),
                "BR": (drone.x, drone.y, self.width_max, self.depth_max),
            }
            area = compute_area_overlap(areas[radar], area)
        # Narrow further if radar info has changed
        if self.radar_info_has_changed:
            for drone_id, radar in self.radar_info.items():
                drone = ME.drones[drone_id]
                old_radar = self.last_turn_radar_info.get(drone_id)
                x_min, y_min, x_max, y_max = area
                if "L" in old_radar and "R" in radar:
                    x_min, x_max = drone.x, drone.x + CREATURE_MOVE_SPEED
                if "R" in old_radar and "L" in radar:
                    x_min, x_max = drone.x - CREATURE_MOVE_SPEED, drone.x
                if "B" in old_radar and "T" in radar:
                    y_min, y_max = drone.y, drone.y + CREATURE_MOVE_SPEED
                if "T" in old_radar and "B" in radar:
                    y_min, y_max = drone.y - CREATURE_MOVE_SPEED, drone.y
                new_area = x_min, y_min, x_max, y_max
                area = compute_area_overlap(new_area, area)
        # Update coordinates
        self.x_min, self.y_min, self.x_max, self.y_max = area
        self.x = (self.x_min + self.x_max) // 2
        self.y = (self.y_min + self.y_max) // 2
        self.vx = 0
        self.vy = 0

    def compute_score_for_drone(self, drone: Drone) -> Tuple[int, float]:
        player = drone.player
        foe = FOE if drone.player is ME else ME
        creatures_to_ignore = player.scanned_or_saved_creatures
        # Skip if already scanned/saved
        if self.id in player.scanned_or_saved_creature_ids:
            return 0, 0
        # Compute score of creature
        distance = DRONE_CREATURE_DISTANCE[(drone.id, self.id)]
        score = 1 / distance
        # Lower score based on points
        value = self.value if self.id in foe.saved_creature_ids else self.value * 2
        score *= 1.2**value
        # Improve score the more similar creatures are scanned (type)
        same_type_scanned = [c for c in creatures_to_ignore if c.type == self.type]
        score *= 1.1 ** len(same_type_scanned)
        # Improve score the more similar creatures are scanned (color)
        same_color_scanned = [c for c in creatures_to_ignore if c.color == self.color]
        score *= 1.1 ** len(same_color_scanned)
        return distance, score

    def update_visible_position(self, x: int, y: int, vx: int, vy: int) -> None:
        self.is_visible = True
        self.last_visible_turn = TURN_COUNT
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        # Update theoretical X
        self.width_min = 0 if self.x < GRID_WIDTH // 2 else GRID_WIDTH // 2
        self.width_max = GRID_WIDTH // 2 if self.x < GRID_WIDTH // 2 else GRID_WIDTH
        # Set grid to exact position
        self.x_min = self.x
        self.x_max = self.x
        self.y_min = self.y
        self.y_max = self.y

    def update_radar_info(self, data: Dict[int, str]) -> None:
        self.last_turn_radar_info = self.radar_info
        self.radar_info = data


# --------------------------------------------------
# Utils
# --------------------------------------------------
def init_creatures(qty: int) -> None:
    for _ in range(qty):
        creature_id, color, _type = [int(j) for j in input().split()]
        creature = Creature(creature_id, color, _type)
        CREATURES_BY_ID[creature_id] = creature


def update_creatures_visibility_from_input() -> None:
    visible_creature_count = int(input())
    visible_ids = set()
    for _ in range(visible_creature_count):
        creature_id, *data = [int(j) for j in input().split()]
        creature = CREATURES_BY_ID.get(creature_id)
        creature.update_visible_position(*data)
        visible_ids.add(creature_id)
    # Update visibility for creatures not visible
    missing_ids = set(CREATURES_BY_ID.keys()) - visible_ids
    for creature_id in missing_ids:
        CREATURES_BY_ID[creature_id].is_visible = False


def update_drone_scans_from_input() -> None:
    drone_scan_count = int(input())
    scans_by_drone_id = {}
    for _ in range(drone_scan_count):
        drone_id, creature_id = [int(j) for j in input().split()]
        scans_by_drone_id.setdefault(drone_id, set()).add(creature_id)
    for drone_id, scans in scans_by_drone_id.items():
        drone = DRONES_BY_ID[drone_id]
        drone.update_scans(scans)


def update_creatures_radar_data_from_input() -> None:
    radar_blip_count = int(input())
    data_per_creature_id: Dict[int, Dict[int, str]] = {}
    for _ in range(radar_blip_count):
        inputs = input().split()
        drone_id = int(inputs[0])
        creature_id = int(inputs[1])
        radar = inputs[2]
        data_per_creature_id.setdefault(creature_id, {}).setdefault(drone_id, radar)
    for creature_id, data in data_per_creature_id.items():
        creature = CREATURES_BY_ID[creature_id]
        creature.update_radar_info(data)


def compute_distance(pos1: Position, pos2: Position) -> int:
    x1, y1 = pos1
    x2, y2 = pos2
    return int(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)


def compute_area_overlap(area1: Area, area2: Area) -> Area:
    x1_min, y1_min, x1_max, y1_max = area1
    x2_min, y2_min, x2_max, y2_max = area2
    x_min = max(x1_min, x2_min)
    y_min = max(y1_min, y2_min)
    x_max = min(x1_max, x2_max)
    y_max = min(y1_max, y2_max)
    return x_min, y_min, x_max, y_max


def increase_area(area: Area, value: int) -> Area:
    x_min, y_min, x_max, y_max = area
    return x_min - value, y_min - value, x_max + value, y_max + value


def debug(message) -> None:
    print(message, file=sys.stderr, flush=True)


def read_input() -> None:
    ME.update_score_from_input()
    FOE.update_score_from_input()
    # Scan
    ME.update_save_count_from_input()
    FOE.update_save_count_from_input()
    # Drones
    ME.update_drones_vitals_from_input()
    FOE.update_drones_vitals_from_input()
    update_drone_scans_from_input()
    # Creatures
    update_creatures_visibility_from_input()
    update_creatures_radar_data_from_input()


def play_turn() -> None:
    for creature in CREATURES_BY_ID.values():
        creature.compute_position_for_turn()
        for drone in DRONES_BY_ID.values():
            distance = compute_distance(drone.position, creature.next_position)
            DRONE_CREATURE_DISTANCE[(drone.id, creature.id)] = distance
    # Play
    for drone_id in ME.ordered_drone_ids:
        drone = ME.drones[drone_id]
        drone.play_turn()


# --------------------------------------------------
# Assumptions
# --------------------------------------------------
CREATURE_MOVE_SPEED = 200
LIGHT_SQUARE_RATIO = 0.8


# --------------------------------------------------
# Game
# --------------------------------------------------
TURN_COUNT = 0
DRONES_BY_ID: Dict[int, Drone] = {}
CREATURES_BY_ID: Dict[int, Creature] = {}
DRONE_CREATURE_DISTANCE: Dict[Tuple[int, int], int] = {}
ME = Player(is_me=True)
FOE = Player(is_me=False)
CREATURE_COUNT = int(input())
init_creatures(CREATURE_COUNT)

while True:
    TURN_COUNT += 1
    read_input()
    if TURN_COUNT == 1:
        DRONES_BY_ID = {**ME.drones, **FOE.drones}
    play_turn()

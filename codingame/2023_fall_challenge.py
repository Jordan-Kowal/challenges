# Built-in
import sys
from typing import Dict, List, Set, Tuple

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


class RadarPosition:
    TOP_LEFT = "TL"
    TOP_RIGHT = "TR"
    BOTTOM_LEFT = "BL"
    BOTTOM_RIGHT = "BR"


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
            drone.update_data(*data)
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

    def __str__(self) -> str:
        return f"Drone {self.id} ({self.position}) for {self.player}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def position(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def best_creature_with_distance(self) -> Tuple["Creature", int]:
        creature_data: List[Tuple[Creature, int, float]] = []
        for creature in CREATURES_BY_ID.values():
            distance, score = creature.compute_score_for_drone(self)
            debug(f"{creature} has score {score} and distance {distance}")
            creature_data.append((creature, distance, score))
        best_creature, distance, _ = min(creature_data, key=lambda x: x[2])
        return best_creature, distance

    def play_turn(self) -> None:
        creature, distance = self.best_creature_with_distance
        x, y = creature.next_position
        activate_light = int(
            LIGHT_MAX_DISTANCE > distance > LIGHT_MIN_DISTANCE
            and self.battery > LIGHT_BATTERY_COST
        )
        self.move(x, y, activate_light)

    def update_data(self, x: int, y: int, emergency: int, battery: int) -> None:
        self.x = x
        self.y = y
        self.emergency = emergency
        self.battery = battery

    @staticmethod
    def move(x: int, y: int, light: int) -> None:
        print(f"MOVE {x} {y} {light}")

    @staticmethod
    def wait(light: int) -> None:
        print(f"WAIT {light}")

    # Action: Back to base but maybe take a creature on the way
    # Action: Back to base directly


class Creature:
    def __init__(self, _id: int, color: int, _type: int) -> None:
        self.id = _id
        self.color = color
        self.type = _type
        self.value: int = VALUE_BY_TYPE[_type]
        self.depth_min, self.depth_max = DEPTHS_BY_TYPE[_type]
        self.x: int = 0
        self.y: int = 0
        self.vx: int = 0
        self.vy: int = 0

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
    def is_visible(self) -> bool:
        return self.x != 0 or self.y != 0

    def compute_position_from_radar(self, data: List[Tuple[int, str]]) -> None:
        if self.is_visible:
            return
        x_min = 0
        x_max = GRID_WIDTH
        y_min = self.depth_min
        y_max = self.depth_max
        for drone_id, radar in data:
            drone = ME.drones[drone_id]
            if radar == RadarPosition.TOP_LEFT:
                x_max = min(x_max, drone.x)
                y_max = min(y_max, drone.y)
            elif radar == RadarPosition.TOP_RIGHT:
                x_min = max(x_min, drone.x)
                y_max = min(y_max, drone.y)
            elif radar == RadarPosition.BOTTOM_LEFT:
                x_max = min(x_max, drone.x)
                y_min = max(y_min, drone.y)
            elif radar == RadarPosition.BOTTOM_RIGHT:
                x_min = max(x_min, drone.x)
                y_min = max(y_min, drone.y)
        self.x = (x_min + x_max) // 2
        self.y = (y_min + y_max) // 2

    def compute_score_for_drone(self, drone: Drone) -> Tuple[int, float]:
        # TODO:
        # value * 2 if not scanned by foe?
        # is_visible?

        player = drone.player
        other_player = FOE if drone.player is ME else ME
        # Skip if already scanned
        if self.id in drone.scanned_creature_ids:
            return 1_000_000, 1_000_000
        # Compute score of creature
        scanned_creatures = [CREATURES_BY_ID[i] for i in drone.scanned_creature_ids]
        distance = compute_distance(drone.position, self.next_position)
        score = distance
        # Improve score if not scanned by foe
        # if self.id not in other_player.scanned_creatures:
        #     score *= 0.8
        # Improve score the more similar creatures are scanned (type)
        similar_type_scanned = sum(
            [int(sc.type == self.type) for sc in scanned_creatures]
        )
        score *= 0.9**similar_type_scanned
        # Improve score the more similar creatures are scanned (color)
        similar_color_scanned = sum(
            [int(sc.color == self.color) for sc in scanned_creatures]
        )
        score *= 0.9**similar_color_scanned
        return distance, score

    def update_position_data(self, x: int, y: int, vx: int, vy: int) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy


# --------------------------------------------------
# Utils
# --------------------------------------------------
def init_creatures(qty: int) -> None:
    for _ in range(qty):
        creature_id, color, _type = [int(j) for j in input().split()]
        creature = Creature(creature_id, color, _type)
        CREATURES_BY_ID[creature_id] = creature


def update_creatures_from_input() -> None:
    visible_creature_count = int(input())
    visible_ids = set()
    for _ in range(visible_creature_count):
        creature_id, *data = [int(j) for j in input().split()]
        creature = CREATURES_BY_ID.get(creature_id)
        creature.update_position_data(*data)
        visible_ids.add(creature_id)
    # If creature not in, reset coordinates
    for creature_id, creature in CREATURES_BY_ID.items():
        if creature_id not in visible_ids:
            creature.update_position_data(0, 0, 0, 0)


def update_drone_scans_from_input() -> None:
    drone_scan_count = int(input())
    scans_by_drone_id = {}
    for _ in range(drone_scan_count):
        drone_id, creature_id = [int(j) for j in input().split()]
        scans_by_drone_id.setdefault(drone_id, set()).add(creature_id)
    for drone_id, scans in scans_by_drone_id.items():
        DRONES_BY_ID[drone_id].scanned_creature_ids = scans


def compute_creatures_positions_from_input() -> None:
    radar_blip_count = int(input())
    data_per_creature_id: Dict[int, List[Tuple[int, str]]] = {}
    for _ in range(radar_blip_count):
        inputs = input().split()
        drone_id = int(inputs[0])
        creature_id = int(inputs[1])
        radar = inputs[2]
        data_per_creature_id.setdefault(creature_id, []).append((drone_id, radar))
    for creature_id, data in data_per_creature_id.items():
        creature = CREATURES_BY_ID[creature_id]
        creature.compute_position_from_radar(data)


def compute_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    x1, y1 = pos1
    x2, y2 = pos2
    return int(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)


def debug(message) -> None:
    print(message, file=sys.stderr, flush=True)


def play_turn() -> None:
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
    update_creatures_from_input()
    compute_creatures_positions_from_input()
    # Play
    for drone_id in ME.ordered_drone_ids:
        drone = ME.drones[drone_id]
        drone.play_turn()


# --------------------------------------------------
# Game
# --------------------------------------------------
DRONES_BY_ID: Dict[int, Drone] = {}
CREATURES_BY_ID: Dict[int, Creature] = {}
ME = Player(is_me=True)
FOE = Player(is_me=False)
CREATURE_COUNT = int(input())
init_creatures(CREATURE_COUNT)

first = True
while True:
    play_turn()
    if first:
        first = False
        DRONES_BY_ID = {**ME.drones, **FOE.drones}

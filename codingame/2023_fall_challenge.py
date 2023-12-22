# Built-in
import sys
from typing import Dict, List, Set, Tuple


class Player:
    def __init__(self) -> None:
        self.score: int = 0
        self.scan_count: int = 0
        self.scanned_creature_ids: Set[int] = set()
        self.drones: Dict[int, Drone] = {}
        self.ordered_drone_ids: List[int] = []

    @property
    def drone_count(self) -> int:
        return len(self.drones)

    @property
    def scanned_creatures(self) -> Set["Creature"]:
        return {CREATURES_BY_ID[i] for i in self.scanned_creature_ids}

    def update_score_from_input(self) -> None:
        self.score = int(input())

    def update_scan_count_from_input(self) -> None:
        self.scan_count = int(input())
        self.scanned_creature_ids = {int(input()) for _ in range(self.scan_count)}

    def update_drones_from_input(self) -> None:
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
    def __init__(
        self,
        player: Player,
        id: int,
    ) -> None:
        self.player = player
        self.id = id
        self.x: int = 0
        self.y: int = 0
        self.emergency: int = 0
        self.battery: int = 0

    @property
    def position(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def best_creature_with_distance(self) -> Tuple["Creature", int]:
        creature_data: List[Creature, int, float] = []
        for creature in CREATURES_BY_ID.values():
            distance, score = creature.compute_score_for_drone(self)
            debug(f"{creature} has score {score} and distance {distance}")
            creature_data.append((creature, distance, score))
        best_creature, *_ = min(creature_data, key=lambda x: x[2])
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


class Creature:
    def __init__(self, id: int, color: int, _type: int) -> None:
        self.id = id
        self.color = color
        self.type = _type
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

    def compute_score_for_drone(self, drone: Drone) -> Tuple[int, float]:
        player = drone.player
        other_player = FOE if drone.player is ME else ME
        # Skip if already scanned
        if self.id in player.scanned_creature_ids:
            return 1_000_000, 1_000_000
        # Compute score of creature
        scanned_creatures = player.scanned_creatures
        distance = compute_distance(drone.position, self.next_position)
        score = distance
        # Improve score if not scanned by foe
        if self.id not in other_player.scanned_creatures:
            score *= 0.8
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

    def update_data(self, x: int, y: int, vx: int, vy: int) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy


def compute_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    x1, y1 = pos1
    x2, y2 = pos2
    return int(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)


def init_creatures(qty: int) -> None:
    for _ in range(qty):
        creature_id, color, _type = [int(j) for j in input().split()]
        creature = Creature(creature_id, color, _type)
        CREATURES_BY_ID[creature_id] = creature


def update_creatures_from_input() -> None:
    visible_creature_count = int(input())
    for _ in range(visible_creature_count):
        creature_id, *data = [int(j) for j in input().split()]
        creature = CREATURES_BY_ID.get(creature_id)
        creature.update_data(*data)


def debug(message) -> None:
    print(message, file=sys.stderr, flush=True)


def update_game_state() -> None:
    # Score
    ME.update_score_from_input()
    FOE.update_score_from_input()
    # Scan
    ME.update_scan_count_from_input()
    FOE.update_scan_count_from_input()
    # Drones
    ME.update_drones_from_input()
    FOE.update_drones_from_input()
    # Later
    drone_scan_count = int(input())
    for i in range(drone_scan_count):
        drone_id, creature_id = [int(j) for j in input().split()]
    # Creatures
    update_creatures_from_input()
    # Later
    radar_blip_count = int(input())
    for i in range(radar_blip_count):
        inputs = input().split()
        drone_id = int(inputs[0])
        creature_id = int(inputs[1])
        radar = inputs[2]


def play_turn() -> None:
    update_game_state()
    for drone_id in ME.ordered_drone_ids:
        drone = ME.drones[drone_id]
        drone.play_turn()


LIGHT_MAX_DISTANCE = 2000
LIGHT_MIN_DISTANCE = 800
LIGHT_BATTERY_COST = 5
CREATURES_BY_ID = {}
ME = Player()
FOE = Player()
CREATURE_COUNT = int(input())
init_creatures(CREATURE_COUNT)

while True:
    play_turn()

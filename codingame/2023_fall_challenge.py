# Built-in
from typing import Dict, List, Set


class Player:
    def __init__(self) -> None:
        self.score: int = 0
        self.scan_count: int = 0
        self.scanned_creatures: Set[int] = set()
        self.drones: Dict[int, Drone] = {}
        self.ordered_drone_ids: List[int] = []

    @property
    def drone_count(self) -> int:
        return len(self.drones)

    def update_score_from_input(self) -> None:
        self.score = int(input())

    def update_scan_count_from_input(self) -> None:
        self.scan_count = int(input())
        self.scanned_creatures = {int(input()) for _ in range(self.scan_count)}

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

    def update_data(self, x: int, y: int, vx: int, vy: int) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy


CREATURES_BY_ID = {}
ME = Player()
FOE = Player()


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


CREATURE_COUNT = int(input())
init_creatures(CREATURE_COUNT)

# game loop
while True:
    update_game_state()
    for drone_id in ME.ordered_drone_ids:
        drone = ME.drones[drone_id]
        drone.move(5000, 5000, 0)

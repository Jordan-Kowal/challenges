# Built-in
import math
import sys
from collections import Counter
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
DRONE_SPEED = 600

CREATURE_SPEED = 200
CREATURE_FLEE_RANGE = 1_400

MONSTER_PASSIVE_SPEED = 270
MONSTER_AGGRO_SPEED = 540
MONSTER_KILL_RANGE = 500

VALUE_BY_TYPE: Dict[int, int] = {-1: 0, 0: 1, 1: 2, 2: 3}
COLOR_COMBO = 3
TYPE_COMBO = 4
DEPTHS_BY_TYPE: Dict[int, Tuple[int, int]] = {
    0: (2_500, 5_000),
    1: (5_000, 7_500),
    2: (7_500, 10_000),
    -1: (2500, 10_000),
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
    def foe(self) -> "Player":
        return FOE if self.is_me else ME

    @property
    def saved_creatures(self) -> Set["Creature"]:
        return {FISHES_BY_IDS[i] for i in self.saved_creature_ids}

    @property
    def scanned_creature_ids(self) -> Set[int]:
        ids = set()
        for drone in self.drones.values():
            ids |= drone.scanned_creature_ids
        return ids

    @property
    def scanned_creatures(self) -> Set["Creature"]:
        return {FISHES_BY_IDS[i] for i in self.scanned_creature_ids}

    @property
    def scanned_or_saved_creature_ids(self) -> Set[int]:
        return self.scanned_creature_ids | self.saved_creature_ids

    @property
    def scanned_or_saved_creatures(self) -> Set["Creature"]:
        return self.scanned_creatures | self.saved_creatures

    @property
    def creature_ids_to_scan(self) -> Set[int]:
        available_ids = {c.id for c in FISHES_BY_IDS.values() if not c.is_gone}
        return available_ids - self.scanned_or_saved_creature_ids

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
        self.is_returning: bool = False

    def __str__(self) -> str:
        return f"Drone {self.id} ({self.position}) for {self.player}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def position(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def is_being_chased(self) -> bool:
        for monster in MONSTERS_BY_IDS.values():
            if not monster.is_visible or not monster.is_aggro:
                continue
            is_closest = all(
                [
                    DRONE_CREATURE_DISTANCE[(self.id, monster.id)]
                    <= DRONE_CREATURE_DISTANCE[(drone_id, monster.id)]
                    for drone_id in DRONES_BY_ID.keys()
                ]
            )
            if is_closest:
                return True
        return False

    @property
    def visible_area(self) -> Area:
        radius = LIGHT_MAX_DISTANCE if self.last_turn_light else LIGHT_MIN_DISTANCE
        amount = int(math.sqrt(math.pi) * radius)
        area = self.x, self.y, self.x, self.y
        return increase_area(area, amount)

    @property
    def best_creatures(self) -> List["Creature"]:
        creature_data: List[Tuple[Creature, float]] = []
        for creature in FISHES_BY_IDS.values():
            score = creature.compute_score_for_drone(self)
            creature_data.append((creature, score))
        creature_data.sort(key=lambda x: x[1], reverse=True)
        return [creature for creature, _ in creature_data]

    def play_turn(self) -> None:
        if self.is_returning and len(self.scanned_creature_ids) > 0:
            return self.go_straight_up()
        self.is_returning = False
        if WIN_IF_RETURN:
            return self.go_straight_up()
        if TURN_COUNT < 4:
            return self.move_to_initial_coordinates()
        if self.emergency > 0:
            return self.wait(0)
        if len(self.player.creature_ids_to_scan) == 0:
            return self.go_straight_up()
        return self.move_to_best_creature()

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

    def move_to_best_creature(self) -> None:
        c1, c2, c3 = self.best_creatures[:3]
        x, y = c1.next_position
        # Maybe activate light
        d1, d2, d3 = [DRONE_CREATURE_DISTANCE[(self.id, c.id)] for c in [c1, c2, c3]]
        light = any([LIGHT_MIN_DISTANCE < d < LIGHT_MAX_DISTANCE for d in [d1, d2, d3]])
        self.move(x, y, int(light))

    def move_to_initial_coordinates(self) -> None:
        x = GRID_WIDTH // 3 if self.x < GRID_WIDTH // 2 else GRID_WIDTH * 2 // 3
        y = self.y + 2000
        self.move(x, y, 0)

    @staticmethod
    def wait(light: int) -> None:
        print(f"WAIT {light}")

    def go_straight_up(self) -> None:
        self.is_returning = True
        fishes_within_range = [
            fish_id
            for fish_id in FISHES_BY_IDS.keys()
            if LIGHT_MIN_DISTANCE
            < DRONE_CREATURE_DISTANCE[(self.id, fish_id)]
            < LIGHT_MAX_DISTANCE
            and fish_id not in self.player.scanned_or_saved_creature_ids
        ]
        light = 1 if len(fishes_within_range) > 0 else 0
        self.move(self.x, 500, light)

    def move(self, x: int, y: int, light: int) -> None:
        monsters_are_close = any(
            [
                DRONE_CREATURE_DISTANCE[(self.id, monster_id)] < 1500
                for monster_id in MONSTERS_BY_IDS.keys()
            ]
        )
        # Maybe check if trajectory is at risk
        attempts = 0
        deg = 30
        while monsters_are_close:
            trajectory = []
            for i in range(TRAJECTORY_STEP_COUNT):
                vx, vy = compute_vx_vy_from_positions(
                    self.position,
                    (x, y),
                    int(DRONE_SPEED * (i + 1) / TRAJECTORY_STEP_COUNT),
                )
                trajectory.append((self.x + vx, self.y + vy))
            if self.is_trajectory_is_safe(trajectory):
                break
            # Update trajectory
            attempts += 1
            rotation = attempts // 2 if attempts % 2 != 0 else -attempts // 2
            x, y = rotate_point_on_circle((self.x, self.y), (x, y), rotation * deg)
            # Surrounded, let it die
            if attempts > 12:
                break
        print(f"MOVE {x} {y} {light}")

    @staticmethod
    def is_trajectory_is_safe(trajectory: List[Position]) -> bool:
        for monster in MONSTERS_BY_IDS.values():
            if not monster.is_visible:
                continue
            if check_if_positions_cross_within_distance(
                trajectory, monster.trajectory, MONSTER_KILL_RANGE + 100
            ):
                return False
        return True


class Creature:
    def __init__(self, _id: int, color: int, _type: int) -> None:
        # Fixed info
        self.id = _id
        self.color = color
        self.type = _type
        self.value: int = VALUE_BY_TYPE[_type]
        self.is_monster = _type == -1
        # Available area
        self.width_min, self.width_max = 0, GRID_WIDTH
        self.depth_min, self.depth_max = DEPTHS_BY_TYPE[_type]
        # Position
        self.x: int = 0
        self.y: int = 0
        self.vx: int = 0
        self.vy: int = 0
        self.is_gone: bool = False
        self.is_visible: bool = False
        self.last_visible_turn: Optional[int] = None
        self.trajectory: List[Position] = []
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
    def is_aggro(self) -> bool:
        return (
            self.is_monster
            and abs(self.vx) + abs(self.vy) > MONSTER_PASSIVE_SPEED * 1.5
        )

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

    @property
    def speed(self) -> int:
        if not self.is_monster:
            return CREATURE_SPEED
        if self.is_aggro:
            return MONSTER_AGGRO_SPEED
        return MONSTER_PASSIVE_SPEED

    def compute_position_for_turn(self) -> None:
        self.trajectory = []
        if self.is_visible or self.is_gone:
            return
        # Update width range based on radar info
        for drone_id, radar in self.radar_info.items():
            drone = ME.drones[drone_id]
            if "L" in radar and drone.x < GRID_WIDTH // 2:
                self.width_min, self.width_max = 0, GRID_WIDTH // 2
            elif "R" in radar and drone.x >= GRID_WIDTH // 2:
                self.width_min, self.width_max = GRID_WIDTH // 2, GRID_WIDTH
        # Compute area from previous but within bounds
        area = increase_area(self.area, CREATURE_SPEED)
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
                    x_min, x_max = drone.x, drone.x + CREATURE_SPEED
                if "R" in old_radar and "L" in radar:
                    x_min, x_max = drone.x - CREATURE_SPEED, drone.x
                if "B" in old_radar and "T" in radar:
                    y_min, y_max = drone.y, drone.y + CREATURE_SPEED
                if "T" in old_radar and "B" in radar:
                    y_min, y_max = drone.y - CREATURE_SPEED, drone.y
                new_area = x_min, y_min, x_max, y_max
                area = compute_area_overlap(new_area, area)
        # Update coordinates
        self.x_min, self.y_min, self.x_max, self.y_max = area
        self.x = (self.x_min + self.x_max) // 2
        self.y = (self.y_min + self.y_max) // 2
        self.vx = 0
        self.vy = 0

    def compute_score_for_drone(self, drone: Drone) -> float:
        # Skip if missing or already scanned/saved or monster
        player = drone.player
        if (
            self.is_gone
            or self.id in player.scanned_or_saved_creature_ids
            or self.is_monster
        ):
            return 0
        # Compute score of creature
        distance = DRONE_CREATURE_DISTANCE[(drone.id, self.id)]
        score = 1_000 / distance
        # Lower score based on points
        foe = FOE if drone.player is ME else ME
        creatures_to_ignore = player.scanned_or_saved_creatures
        value = self.value if self.id in foe.saved_creature_ids else self.value * 2
        score *= 1.3**value
        # Improve score the more similar creatures are scanned (type)
        same_type_scanned = [c for c in creatures_to_ignore if c.type == self.type]
        score *= 1.1 ** len(same_type_scanned)
        # Improve score the more similar creatures are scanned (color)
        same_color_scanned = [c for c in creatures_to_ignore if c.color == self.color]
        score *= 1.1 ** len(same_color_scanned)
        return score

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

    def compute_trajectory_for_turn(self) -> None:
        next_position = self.x + self.vx, self.y + self.vy
        speed = self.speed
        track: List[Position] = []
        for i in range(TRAJECTORY_STEP_COUNT):
            vx, vy = compute_vx_vy_from_positions(
                self.position,
                next_position,
                int(speed * (i + 1) / TRAJECTORY_STEP_COUNT),
            )
            track.append((self.x + vx, self.y + vy))
        self.trajectory = track


# --------------------------------------------------
# Utils
# --------------------------------------------------
def init_creatures(qty: int) -> None:
    for _ in range(qty):
        creature_id, color, _type = [int(j) for j in input().split()]
        creature = Creature(creature_id, color, _type)
        ALL_CREATURES_BY_ID[creature_id] = creature
        if _type == -1:
            MONSTERS_BY_IDS[creature_id] = creature
        else:
            FISHES_BY_IDS[creature_id] = creature


def update_creatures_visibility_from_input() -> None:
    visible_creature_count = int(input())
    visible_ids = set()
    for _ in range(visible_creature_count):
        creature_id, *data = [int(j) for j in input().split()]
        creature = ALL_CREATURES_BY_ID.get(creature_id)
        creature.update_visible_position(*data)
        visible_ids.add(creature_id)
    # Update visibility for creatures not visible
    missing_ids = set(ALL_CREATURES_BY_ID.keys()) - visible_ids
    for creature_id in missing_ids:
        ALL_CREATURES_BY_ID[creature_id].is_visible = False


def update_drone_scans_from_input() -> None:
    drone_scan_count = int(input())
    scans_by_drone_id = {}
    for _ in range(drone_scan_count):
        drone_id, creature_id = [int(j) for j in input().split()]
        scans_by_drone_id.setdefault(drone_id, set()).add(creature_id)
    for drone_id, scans in scans_by_drone_id.items():
        drone = DRONES_BY_ID[drone_id]
        drone.update_scans(scans)
    missing_drone_ids = set(DRONES_BY_ID.keys()) - set(scans_by_drone_id.keys())
    for drone_id in missing_drone_ids:
        drone = DRONES_BY_ID[drone_id]
        drone.update_scans(set())


def update_creatures_radar_data_from_input() -> None:
    radar_blip_count = int(input())
    data_per_creature_id: Dict[int, Dict[int, str]] = {}
    for _ in range(radar_blip_count):
        inputs = input().split()
        drone_id = int(inputs[0])
        creature_id = int(inputs[1])
        radar = inputs[2]
        data_per_creature_id.setdefault(creature_id, {}).setdefault(drone_id, radar)
    missing_ids = set(ALL_CREATURES_BY_ID.keys()) - set(data_per_creature_id.keys())
    for creature_id in missing_ids:
        creature = ALL_CREATURES_BY_ID[creature_id]
        creature.is_gone = True
    for creature_id, data in data_per_creature_id.items():
        creature = ALL_CREATURES_BY_ID[creature_id]
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


def compute_types_combo(creature_ids: Set[int]) -> Set[int]:
    counter = Counter([ALL_CREATURES_BY_ID[i].type for i in creature_ids])
    return {k for k, v in counter.items() if v == 4}


def compute_colors_combo(creature_ids: Set[int]) -> Set[int]:
    counter = Counter([ALL_CREATURES_BY_ID[i].color for i in creature_ids])
    return {k for k, v in counter.items() if v == 3}


def compute_new_score(
    current_score: int,
    saved_ids: Set[int],
    scanned_ids: Set[int],
    foe_saved_ids: Set[int],
) -> int:
    score = current_score
    # Compute new fishes
    for id_ in scanned_ids:
        if id_ in saved_ids:
            continue
        value = FISHES_BY_IDS[id_].value
        score += value * 2 if id_ not in foe_saved_ids else value
    # Compute new type combos
    foe_current_types = compute_types_combo(foe_saved_ids)
    my_current_types = compute_types_combo(saved_ids)
    my_potential_types = compute_types_combo(scanned_ids)
    my_new_types = my_potential_types - my_current_types
    for type_ in my_new_types:
        value = TYPE_COMBO * 2 if type_ not in foe_current_types else TYPE_COMBO
        score += value
    # Compute new color combos
    foe_current_colors = compute_colors_combo(foe_saved_ids)
    my_current_colors = compute_colors_combo(saved_ids)
    my_potential_colors = compute_colors_combo(scanned_ids)
    my_new_colors = my_potential_colors - my_current_colors
    for color in my_new_colors:
        value = COLOR_COMBO * 2 if color not in foe_current_colors else COLOR_COMBO
        score += value
    return score


def check_if_returning_wins() -> bool:
    all_fishes = set(FISHES_BY_IDS.values())
    available_fish_ids = {c.id for c in all_fishes if not c.is_gone}
    my_score_after_save = compute_new_score(
        ME.score, ME.saved_creature_ids, ME.scanned_creature_ids, FOE.saved_creature_ids
    )
    enemy_best_potential_score_after_my_save = compute_new_score(
        FOE.score,
        FOE.saved_creature_ids,
        available_fish_ids | FOE.scanned_creature_ids,
        ME.saved_creature_ids | ME.scanned_creature_ids,
    )
    my_final_score = compute_new_score(
        my_score_after_save,
        ME.saved_creature_ids | ME.scanned_creature_ids,
        available_fish_ids,
        available_fish_ids | FOE.saved_creature_ids,
    )
    return my_final_score > enemy_best_potential_score_after_my_save


def debug(message) -> None:
    print(message, file=sys.stderr, flush=True)


def check_if_positions_cross_within_distance(
    trajectory1: List[Position], trajectory2: List[Position], distance: int
) -> bool:
    for pos1, pos2 in zip(trajectory1, trajectory2):
        if compute_distance(pos1, pos2) < distance:
            return True
    return False


def compute_vx_vy_from_positions(
    pos1: Position, pos2: Position, distance: int
) -> Tuple[int, int]:
    if pos1 == pos2:
        return 0, 0
    x1, y1 = pos1
    x2, y2 = pos2
    dx = x2 - x1
    dy = y2 - y1
    dh = (dx**2 + dy**2) ** 0.5
    # TODO: Extract this for performance
    ratio = dh / distance
    return int(dx / ratio), int(dy / ratio)


def rotate_point_on_circle(center: Position, point: Position, degrees: int) -> Position:
    x, y = center
    x2, y2 = point
    # Convert the angle from degrees to radians
    angle_rad = math.radians(degrees)
    # Translate the point to the origin
    x2_translated = x2 - x
    y2_translated = y2 - y
    # Perform the rotation
    x2_rotated = x2_translated * math.cos(angle_rad) - y2_translated * math.sin(
        angle_rad
    )
    y2_rotated = x2_translated * math.sin(angle_rad) + y2_translated * math.cos(
        angle_rad
    )
    # Translate the point back
    x2_new = x2_rotated + x
    y2_new = y2_rotated + y
    return int(x2_new), int(y2_new)


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
    # Compute distance between drones and creatures
    for creature in ALL_CREATURES_BY_ID.values():
        creature.compute_position_for_turn()
        for drone in DRONES_BY_ID.values():
            distance = compute_distance(drone.position, creature.next_position)
            DRONE_CREATURE_DISTANCE[(drone.id, creature.id)] = distance
    # Compute monsters progress
    for monster in MONSTERS_BY_IDS.values():
        if monster.is_visible:
            monster.compute_trajectory_for_turn()
    # Saving now might make us win
    if check_if_returning_wins():
        for drone in ME.drones.values():
            drone.is_returning = True
    # Play
    for drone_id in ME.ordered_drone_ids:
        drone = ME.drones[drone_id]
        drone.play_turn()


# --------------------------------------------------
# Params
# --------------------------------------------------
TRAJECTORY_STEP_COUNT = 10


# --------------------------------------------------
# Game
# --------------------------------------------------
DRONES_BY_ID: Dict[int, Drone] = {}
ALL_CREATURES_BY_ID: Dict[int, Creature] = {}
FISHES_BY_IDS: Dict[int, Creature] = {}
MONSTERS_BY_IDS: Dict[int, Creature] = {}
MISSING_CREATURE_IDS: Set[int] = set()
DRONE_CREATURE_DISTANCE: Dict[Tuple[int, int], int] = {}
WIN_IF_RETURN = False

ME = Player(is_me=True)
FOE = Player(is_me=False)

CREATURE_COUNT = int(input())
init_creatures(CREATURE_COUNT)

TURN_COUNT = 0
while True:
    TURN_COUNT += 1
    read_input()
    if TURN_COUNT == 1:
        DRONES_BY_ID = {**ME.drones, **FOE.drones}
    play_turn()

import random
import math
from config import DUNGEON_WIDTH, DUNGEON_HEIGHT
from core.objects.stairs import Stairs
from core.systems.tile import factory

class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)

    def intersects(self, other):
        return (
            self.x < other.x + other.width and
            self.x + self.width > other.x and
            self.y < other.y + other.height and
            self.y + self.height > other.y
        )

class DungeonGenerator:
    def __init__(self, dungeon, width=DUNGEON_WIDTH, height=DUNGEON_HEIGHT,
                 num_rooms=5, room_min_size=5, room_max_size=20, wiggly=0.2):
        self.width = width
        self.height = height
        self.num_rooms = num_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.rooms = []
        self.grid = None
        self.dungeon = dungeon
        self.wiggly = wiggly
        self.wall_list = []
        for tile_def in factory.tile_classes:
            if factory.tile_properties[tile_def]['wall'] == 1:
                self.wall_list.append(tile_def)

        self.floor_list = []
        for tile_def in factory.tile_classes:
            if factory.tile_properties[tile_def]['wall'] == 0:
                self.floor_list.append(tile_def)

        
        self.wall_weights = []
        for tile_def in factory.tile_classes:
            if factory.tile_properties[tile_def]['wall'] == 1:
                self.wall_weights.append(factory.tile_properties[tile_def]['rarity'])

        self.floor_weights = []
        for tile_def in factory.tile_classes:
            if factory.tile_properties[tile_def]['wall'] == 0:
                self.floor_weights.append(factory.tile_properties[tile_def]['rarity'])

    def generate(self):
        self.grid = [[random.choices(self.wall_list, self.wall_weights, k=1)[0] for _ in range(self.width)] for _ in range(self.height)]

        self.generate_rooms()
        self.connect_rooms_mst()
        self.soften_edges()
        self.place_goal()

        return self.grid, self.rooms

    def generate_rooms(self):
        for _ in range(self.num_rooms):
            w = random.randint(self.room_min_size, self.room_max_size)
            h = random.randint(self.room_min_size, self.room_max_size)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            new_room = Room(x, y, w, h)
            if any(new_room.intersects(r) for r in self.rooms):
                continue

            self.rooms.append(new_room)
            self.create_room_tiles(new_room)

    def create_room_tiles(self, room):
        tile = random.choices(self.floor_list, self.floor_weights, k=1)[0]
        for ry in range(room.y, room.y + room.height):
            for rx in range(room.x, room.x + room.width):
                self.grid[ry][rx] = tile

    def connect_rooms_mst(self):
        if len(self.rooms) <= 1:
            return

        centers = [r.center() for r in self.rooms]

        edges = []
        for i in range(len(centers)):
            for j in range(i+1, len(centers)):
                x1, y1 = centers[i]
                x2, y2 = centers[j]
                dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                edges.append((dist, i, j))
        edges.sort(key=lambda e: e[0])

        parent = list(range(len(centers)))
        def find_set(v):
            while v != parent[v]:
                v = parent[v]
            return v
        def union_set(a, b):
            a = find_set(a)
            b = find_set(b)
            if a != b:
                parent[b] = a

        mst_edges = []
        for dist, i, j in edges:
            if find_set(i) != find_set(j):
                union_set(i, j)
                mst_edges.append((i, j))
                if len(mst_edges) == len(centers)-1:
                    break

        for (i, j) in mst_edges:
            x1, y1 = centers[i]
            x2, y2 = centers[j]
            self.carve_corridor(x1, y1, x2, y2)

    def carve_corridor(self, x1, y1, x2, y2):
        # Random walk approach to create a corridor with slight randomness.
        x, y = x1, y1
        nearby_floor = self.find_nearest_floor(x, y)
        tile_to_place = nearby_floor if nearby_floor else random.choices(self.floor_list, self.floor_weights, k=1)[0]
        self.grid[y][x] = nearby_floor

        # Define how "wiggly" the corridor is, probability of deviating
        wiggle_chance = self.wiggly

        while (x, y) != (x2, y2):
            dx = x2 - x
            dy = y2 - y

            # Decide which axis to move along.
            horizontal_priority = abs(dx) > abs(dy)

            if horizontal_priority:
                # Mostly move in x-direction
                step_x = 1 if dx > 0 else -1
                step_y = 0
            else:
                # Mostly move in y-direction
                step_x = 0
                step_y = 1 if dy > 0 else -1

            # With some probability, deviate from the chosen direction
            if random.random() < wiggle_chance:
                # Attempt a perpendicular move
                if horizontal_priority:
                    # Instead of moving horizontally, try up or down
                    step_x = 0
                    step_y = random.choice([1, -1])
                else:
                    # Instead of moving vertically, try left or right
                    step_y = 0
                    step_x = random.choice([1, -1])

            # Make sure we don't go out of bounds
            nx, ny = x + step_x, y + step_y
            if 0 <= nx < self.width and 0 <= ny < self.height:
                x, y = nx, ny
                nearby_floor = self.find_nearest_floor(x, y)
                tile_to_place = nearby_floor if nearby_floor else random.choices(self.floor_list, self.floor_weights, k=1)[0]
                self.grid[y][x] = tile_to_place

                # Occasionally carve adjacent tiles to break the straight line
                if random.random() < 0.1:
                    # Try carving a side tile
                    for side_x, side_y in [(1,0),(-1,0),(0,1),(0,-1)]:
                        sx, sy = x + side_x, y + side_y
                        if 0 <= sx < self.width and 0 <= sy < self.height:
                            # With a small chance, carve a neighboring tile
                            if random.random() < 0.3:
                                nearby_floor = self.find_nearest_floor(x, y)
                                tile_to_place = nearby_floor if nearby_floor else random.choices(self.floor_list, self.floor_weights, k=1)[0]
                                self.grid[sy][sx] = tile_to_place
            else:
                # If we go out of bounds, break (shouldn't normally happen if rooms are inside bounds)
                break

    def soften_edges(self):
        # We want a simple CA that never turns floor back into wall.
        # It can only carve more floor from walls under certain conditions.
        # Let's say:
        # - If a wall has <= death_limit wall neighbors, it becomes floor.
        # - Floors stay floors no matter what.

        iterations = 1
        birth_limit = 5
        death_limit = 5

        for _ in range(iterations):
            new_grid = [[cell for cell in row] for row in self.grid]

            for y in range(self.height):
                for x in range(self.width):
                    wall_count = self.count_adjacent_walls(x, y)

                    if self.grid[y][x] in self.floor_list:
                        new_grid[y][x] = self.grid[y][x]
                    else:
                        # It's a wall, decide if we should turn it into floor.
                        # If it has very few wall neighbors, turn it into floor.
                        nearby_floor = self.find_nearest_floor(x, y)
                        tile_to_place = nearby_floor if nearby_floor else random.choices(self.floor_list, self.floor_weights, k=1)[0]
                        nearby_wall = self.find_nearest_wall(x, y)
                        wall_to_place = nearby_wall if nearby_wall else random.choices(self.wall_list, self.wall_weights, k=1)[0]
                        if wall_count <= death_limit:
                            new_grid[y][x] = tile_to_place
                        else:
                            new_grid[y][x] = wall_to_place

            self.grid = new_grid

    def count_adjacent_walls(self, tile_x, tile_y):
        wall_count = 0
        for j in range(-1, 2):
            for i in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = tile_x + i, tile_y + j
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx] in self.wall_list:
                        wall_count += 1
                else:
                    # Out-of-bounds considered wall
                    wall_count += 1
        return wall_count
    
    def find_nearest_floor(self, tile_x, tile_y):
        for j in range(-1, 2):
            for i in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = tile_x + i, tile_y + j
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx] in self.floor_list:
                        return self.grid[ny][nx]
                else:
                    continue
        return None
    
    def find_nearest_wall(self, tile_x, tile_y):
        for j in range(-1, 2):
            for i in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = tile_x + i, tile_y + j
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx] in self.wall_list:
                        return self.grid[ny][nx]
                else:
                    continue
        return None
    
    def place_goal(self):
        # Get the last room
        last_room = self.rooms[-1]
        room_center_x, room_center_y = last_room.center()

        # room.center() gives integer coordinates inside the room,
        # which should be a floor tile since we carved the room.
        goal_x, goal_y = room_center_x, room_center_y

        # Place the stairs at this center tile
        self.goal = Stairs(goal_x, goal_y)
        self.dungeon.add_entity(self.goal)


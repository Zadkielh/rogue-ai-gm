import os
import pygame
import random

import yaml
from config import *
from core.systems.dungeon_generator import DungeonGenerator

from core.systems.tile import factory
from core.objects.enemy import enemy_factory
from core.objects.item import item_factory
from core.objects.statics import static_factory

class Dungeon:
    def __init__(self, num_rooms=5, room_min_size=5, room_max_size=10, width=DUNGEON_WIDTH, height=DUNGEON_HEIGHT):
        self.width = width
        self.height = height
        self.tiles = pygame.sprite.Group()
        self.all_entities = []
        
        self.num_rooms = 5
        self.room_min_size = 5
        self.room_max_size = 10

        self.wiggly = 0.2

        self.theme = "None"
        self.name = "Dungeon"

        self.load_dungeon_settings(os.path.abspath("src/config/dungeon.yaml"))

        generator = DungeonGenerator(self, width=self.width, height=self.height,
                                     num_rooms=self.num_rooms, room_min_size=self.room_min_size,
                                     room_max_size=self.room_max_size, wiggly=self.wiggly)
        self.grid, self.rooms = generator.generate()

        self.convert_grid_to_tiles()

        # Spawn Enemies, Items, and Statics
        for enemy_def in enemy_factory.enemy_definitions:
            for _ in range(enemy_def.get('amount', 0)):
                self.spawn_enemy(enemy_def['type'])

        for item_def in item_factory.item_definitions:
            for _ in range(item_def.get('amount', 0)):
                self.spawn_item(item_def['name'])

        for static_def in static_factory.enemy_definitions:
            for _ in range(static_def.get('amount', 0)):
                self.spawn_static(static_def['type'])

    def convert_grid_to_tiles(self):
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.grid[y][x]
                if tile_type:  # If not None
                    tile = factory.create_tile(tile_type, x, y)
                    self.tiles.add(tile)
                    self.grid[y][x] = tile  # Replace string with actual Tile object

    def get_tiles(self):
        return self.tiles

    def find_valid_spawn_points(self):
        valid_points = []
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                if tile and getattr(tile, 'collide', None) == 0:
                    valid_points.append((x, y))
        return valid_points

    def get_random_spawn_point(self):
        valid_points = self.find_valid_spawn_points()
        return random.choice(valid_points)
    
    def find_spawn_point(self):
        entry_room = self.rooms[0]
        return entry_room.center()
    
    def is_blocked_tile(self, tile_x, tile_y):
        """Check if a tile is blocked (e.g., a wall)."""
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            tile = self.grid[tile_y][tile_x]
            return tile and tile.wall == 1
        return True  # Out of bounds is blocked

    def check_collision(self, entity):
        # Determine the range of tiles the entity's rect covers
        left_tile = entity.rect.left // TILE_SIZE_X
        # Subtract 1 from right and bottom calculations:
        right_tile = (entity.rect.right - 1) // TILE_SIZE_X  
        top_tile = entity.rect.top // TILE_SIZE_Y
        bottom_tile = (entity.rect.bottom - 1) // TILE_SIZE_Y

        for ty in range(top_tile, bottom_tile + 1):
            for tx in range(left_tile, right_tile + 1):
                if 0 <= tx < self.width and 0 <= ty < self.height:
                    tile = self.grid[ty][tx]
                    if tile and tile.wall == 1:
                        return True
                else:
                    return True  # Out of bounds considered blocked

        return False
    
    def add_entity(self, entity):
        self.all_entities.append(entity)

    def spawn_enemy(self, enemy_name):
        x, y = self.get_random_spawn_point()
        entity = enemy_factory.create_enemy(enemy_name, x, y, self)
        self.add_entity(entity)
        return entity

    def spawn_item(self, item_name):
        x, y = self.get_random_spawn_point()
        item_entity = item_factory.create_item(item_name, x, y, self)
        self.add_entity(item_entity)
        return item_entity
    
    def spawn_static(self, static_type):
        x, y = self.get_random_spawn_point()
        static_entity = static_factory.create_static(static_type, x, y, self)
        print("Spawning static entity at", x, y)
        self.add_entity(static_entity)
        return static_entity
    
    def load_dungeon_settings(self, file_path):
        """Load item definitions from a YAML file."""
        with open(file_path, 'r') as file:
            item_data = yaml.safe_load(file)
            if 'dungeon' in item_data:
                self.rooms = item_data['dungeon'][0]['rooms']
                self.room_min_size = item_data['dungeon'][0]['room_min_size']
                self.room_max_size = item_data['dungeon'][0]['room_max_size']
                self.width = item_data['dungeon'][0]['width']
                self.height = item_data['dungeon'][0]['height']
                self.theme = item_data['dungeon'][0]['theme']
                self.wiggly = item_data['dungeon'][0]['wiggly']
                self.name = item_data['dungeon'][0]['name']
            else:
                raise ValueError("No 'items' key found in YAML.")
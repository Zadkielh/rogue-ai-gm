import pygame
import yaml
import os
from config import TILE_SIZE_X, TILE_SIZE_Y

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_x, tile_y, tile_type, color, collide=0, wall=0, rarity=50):
        super().__init__()
        self.tile_x = tile_x  # Tile coordinate x
        self.tile_y = tile_y  # Tile coordinate y
        self.tile_type = tile_type
        self.color = color
        self.components = []
        self.collide = collide
        self.wall = wall
        self.rarity = rarity

        # Convert tile coordinates to pixel coordinates for rendering
        pixel_x = tile_x * TILE_SIZE_X
        pixel_y = tile_y * TILE_SIZE_Y
        self.image = pygame.Surface((TILE_SIZE_X, TILE_SIZE_Y))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(pixel_x, pixel_y))

    def add_component(self, component):
        self.components.append(component)

    def remove_component(self, component_name):
        self.components = [comp for comp in self.components if comp.name != component_name]

    def get_component(self, component_name):
        for comp in self.components:
            if comp.name == component_name:
                return comp
        return None

    def has_component(self, component_name):
        return any(comp.name == component_name for comp in self.components)


class TileFactory:
    def __init__(self):
        self.tile_classes = {}
        self.tile_properties = {}
        self.tile_instances = []

    def load_tile_definitions(self, file_path):
        """Load tile definitions from a YAML file."""
        with open(file_path, 'r') as file:
            tile_data = yaml.safe_load(file)
            for tile in tile_data['tiles']:
                name = tile['name']
                color = tile['color']
                collide = tile['collide']
                wall = tile['wall']
                rarity = tile['rarity']
                self.register_tile(name, Tile, tuple(color), collide, wall, rarity)

    def register_tile(self, tile_name, tile_class, color, collide, wall, rarity):
        self.tile_classes[tile_name] = tile_class
        self.tile_properties[tile_name] = {}
        self.tile_properties[tile_name]["color"] = color
        self.tile_properties[tile_name]["collide"] = collide
        self.tile_properties[tile_name]["wall"] = wall
        self.tile_properties[tile_name]["rarity"] = rarity

    def create_tile(self, tile_type, tile_x, tile_y):
        """Create a tile instance in tile units."""
        if tile_type in self.tile_classes:
            color = self.tile_properties[tile_type]["color"]
            collide = self.tile_properties[tile_type]["collide"]
            wall = self.tile_properties[tile_type]["wall"]
            rarity = self.tile_properties[tile_type]["rarity"]
            new_tile = self.tile_classes[tile_type](tile_x, tile_y, tile_type, color, collide, wall, rarity)
            self.tile_instances.append(new_tile)
            return new_tile
        else:
            raise ValueError(f"Tile type '{tile_type}' is not registered.")

    def get_all_instances(self):
        """Return all created tile instances."""
        return self.tile_instances

factory = TileFactory()
factory.load_tile_definitions(os.path.abspath("src/config/tiles.yaml"))


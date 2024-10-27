# src/core/dungeon.py
import pygame
from config import *
from core.systems.tile import factory

# Create a map layout with boundary walls
TILE_MAP = [
    ["wall" if col == 0 or col == NUM_TILES_X - 1 or row == 0 or row == NUM_TILES_Y - 1 else "floor" for col in range(NUM_TILES_X)]
    for row in range(NUM_TILES_Y)
]
class Dungeon:
    def __init__(self):
        self.tiles = pygame.sprite.Group()
        self.create_map()

    def create_map(self):
        for row_index, row in enumerate(TILE_MAP):
            for col_index, tile_type in enumerate(row):
                x, y = col_index * TILE_SIZE_X, row_index * TILE_SIZE_Y
                tile = factory.create_tile(tile_type, x, y)
                self.tiles.add(tile)

    def check_collision(self, entity):
        # Check if the entity is colliding with any walls
        for tile in self.tiles:
            if tile.tile_type == "wall" and entity.rect.colliderect(tile.rect):
                return True
        return False

    def draw(self, screen, camera):
        for tile in self.tiles:
            # Draw tiles using the camera offset
            screen.blit(tile.image, camera.apply(tile))

    @property
    def width(self):
        # Total width of the dungeon in pixels
        return NUM_TILES_X * TILE_SIZE_X

    @property
    def height(self):
        # Total height of the dungeon in pixels
        return NUM_TILES_Y * TILE_SIZE_Y
    
    def alter_tile(self, x, y, new_tile_type):
        # Find the tile at the given coordinates
        for tile in list(self.tiles):
            if tile.x == x and tile.y == y:
                # Remove the old tile from the group
                self.tiles.remove(tile)
                # Create a new tile of the specified type
                new_tile = factory.create_tile(new_tile_type, x, y)
                self.tiles.add(new_tile)
                print(f"Altered tile at ({x}, {y}) to type: {new_tile.tile_type}")
                return new_tile
        print(f"No tile found at ({x}, {y}) to alter.")
        return None
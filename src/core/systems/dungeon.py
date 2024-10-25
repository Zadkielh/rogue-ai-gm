# src/core/dungeon.py
import pygame
from config import *

# Create a map layout with boundary walls
TILE_MAP = [
    [1 if col == 0 or col == NUM_TILES_X - 1 or row == 0 or row == NUM_TILES_Y - 1 else 0 for col in range(NUM_TILES_X)]
    for row in range(NUM_TILES_Y)
]

class Dungeon:
    def __init__(self):
        self.tiles = pygame.sprite.Group()
        self.create_map()

    def create_map(self):
        for row_index, row in enumerate(TILE_MAP):
            for col_index, tile in enumerate(row):
                if tile == 1:
                    Wall(self.tiles, col_index * TILE_SIZE_X, row_index * TILE_SIZE_Y)
                else:
                    Floor(self.tiles, col_index * TILE_SIZE_X, row_index * TILE_SIZE_Y)

    def check_collision(self, entity):
        # Check if the entity is colliding with any walls
        for tile in self.tiles:
            if isinstance(tile, Wall) and entity.rect.colliderect(tile.rect):
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
    

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, x, y, color):
        super().__init__()
        self.tile_type = tile_type
        self.image = pygame.Surface((TILE_SIZE_X, TILE_SIZE_Y))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Wall(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = pygame.Surface((TILE_SIZE_X, TILE_SIZE_Y))
        self.image.fill((255, 0, 0))  # Red color for wall
        self.rect = self.image.get_rect(topleft=(x, y))

class Floor(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = pygame.Surface((TILE_SIZE_X, TILE_SIZE_Y))
        self.image.fill((100, 100, 100))  # Gray color for floor
        self.rect = self.image.get_rect(topleft=(x, y))

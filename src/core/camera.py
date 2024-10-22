# src/core/camera.py
import pygame
from config import TILE_SIZE_X, TILE_SIZE_Y, SCREEN_WIDTH, SCREEN_HEIGHT

class Camera:
    def __init__(self, view_distance, dungeon_width, dungeon_height):
        self.view_distance = view_distance

        # Calculate viewport dimensions based on tile size and view distance
        self.viewport_width = view_distance * TILE_SIZE_X
        self.viewport_height = view_distance * TILE_SIZE_Y

        self.camera = pygame.Rect(0, 0, self.viewport_width, self.viewport_height)
        self.dungeon_width = dungeon_width * TILE_SIZE_X
        self.dungeon_height = dungeon_height * TILE_SIZE_Y

    def apply(self, entity):
        # Apply the camera offset to the entity's position
        rect = entity.rect.copy()
        rect.x -= self.camera.x
        rect.y -= self.camera.y
        return rect

    def update(self, target):
        # Center the camera on the player
        x = target.rect.centerx - self.viewport_width // 2
        y = target.rect.centery - self.viewport_height // 2

        # Ensure the camera doesn't go outside of the dungeon bounds
        x = max(0, min(x, self.dungeon_width - self.viewport_width))
        y = max(0, min(y, self.dungeon_height - self.viewport_height))

        self.camera.topleft = (x, y)


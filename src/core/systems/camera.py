import pygame
from config import TILE_SIZE_X, TILE_SIZE_Y

class Camera:
    def __init__(self, view_distance, dungeon_width, dungeon_height):
        self.view_distance = view_distance

        # Camera viewport size in tiles
        self.viewport_width = view_distance
        self.viewport_height = view_distance

        # Actual dungeon dimensions in tiles
        self.dungeon_width = dungeon_width
        self.dungeon_height = dungeon_height

        # Camera dimensions in pixels
        camera_width_pixels = self.viewport_width * TILE_SIZE_X
        camera_height_pixels = self.viewport_height * TILE_SIZE_Y

        # Camera position (in pixels)
        self.camera = pygame.Rect(0, 0, camera_width_pixels, camera_height_pixels)

    def apply(self, entity):
        """Apply the camera offset to the entity's position for rendering."""
        rect = entity.rect.copy()
        rect.x -= self.camera.x
        rect.y -= self.camera.y
        return rect

    def update(self, target):
        """Center the camera on the target, using float pixel coordinates for smooth movement."""

        # Player position in pixels
        player_pixel_x = target.x * TILE_SIZE_X
        player_pixel_y = target.y * TILE_SIZE_Y

        # Calculate desired camera top-left so that player is centered
        # Half the viewport size in pixels
        half_w = self.camera.width / 2
        half_h = self.camera.height / 2

        desired_x = player_pixel_x - half_w
        desired_y = player_pixel_y - half_h

        # Clamp the camera within the dungeon boundaries in pixel coordinates
        max_x = self.dungeon_width * TILE_SIZE_X - self.camera.width
        max_y = self.dungeon_height * TILE_SIZE_Y - self.camera.height

        desired_x = max(0, min(desired_x, max_x))
        desired_y = max(0, min(desired_y, max_y))

        self.camera.topleft = (desired_x, desired_y)

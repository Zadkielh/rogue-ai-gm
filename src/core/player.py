# src/core/player.py
import pygame
from config import *

class Player(pygame.sprite.Sprite):
    def __init__(self, dungeon):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE_X, TILE_SIZE_Y))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=(TILE_SIZE_X * 3, TILE_SIZE_Y * 3))
        self.speed = 5
        self.dungeon = dungeon  # Reference to the dungeon for collision

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed

        self.move(dx, dy)

    def move(self, dx, dy):
        # Move the player and check for collisions
        self.rect.x += dx
        if self.dungeon.check_collision(self):
            self.rect.x -= dx  # Undo movement if collision

        self.rect.y += dy
        if self.dungeon.check_collision(self):
            self.rect.y -= dy  # Undo movement if collision

    def draw(self, screen):
        screen.blit(self.image, self.rect)

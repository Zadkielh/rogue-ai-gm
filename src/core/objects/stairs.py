import pygame
from config import TILE_SIZE_X, TILE_SIZE_Y

class Stairs(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE_X, TILE_SIZE_Y))
        self.image.fill((155, 0, 255))
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE_X, y * TILE_SIZE_Y))
        self.x = x
        self.y = y

        self.emits_light = True
        self.light_radius = 1

        self.collide = False

        print(f"Stairs created at ({self.x}, {self.y})")

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def __emits_light__(self):
        return True
    
    def distance_to(self, entity):
        return abs(self.x - entity.x) + abs(self.y - entity.y)

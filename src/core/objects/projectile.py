import pygame
from config import TILE_SIZE_X, TILE_SIZE_Y

class Projectile(pygame.sprite.Sprite):
    def __init__(self, dungeon, x, y, dx, dy, speed=0.2, range_in_tiles=10, damage=2, color=(255, 255, 0), acceleration=0.0, owner=None):
        super().__init__()
        self.dungeon = dungeon
        self.x = float(x)
        self.y = float(y)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.range = range_in_tiles
        self.damage = damage
        self.distance_traveled = 0
        self.emits_light = True
        self.light_radius = 1

        self.owner = owner

        self.acceleration = acceleration

        self.collide = True

        self.image = pygame.Surface((TILE_SIZE_X, TILE_SIZE_Y))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(int(self.x * TILE_SIZE_X), int(self.y * TILE_SIZE_Y)))

    def update(self):
        old_x, old_y = self.x, self.y
        self.x += self.dx * self.speed * (self.acceleration * self.distance_traveled + 1)
        self.y += self.dy * self.speed * (self.acceleration * self.distance_traveled + 1)
        self.distance_traveled += self.speed * (self.acceleration * self.distance_traveled + 1)

        # Update position
        self.rect.topleft = (int(self.x * TILE_SIZE_X), int(self.y * TILE_SIZE_Y))

        # Check if out of range
        if self.distance_traveled >= self.range:
            self.destroy()
            return

        # Check if hits wall
        if self.dungeon.is_blocked_tile(int(self.x), int(self.y)):
            self.destroy()
            return
        
        if abs(old_x - self.x) < 0.01 and abs(old_y - self.y) < 0.01:
            self.destroy()
            return

        # Check collision with entities (e.g. enemies)
        for ent in self.dungeon.all_entities:
            if ent is not self and ent.rect.colliderect(self.rect) and hasattr(ent, 'take_damage'):
                # Deal damage to the entity and destroy the projectile
                if self.owner is not ent:
                    ent.take_damage(self.damage, self.owner)
                    self.destroy()
                    return

    def destroy(self):
        if self in self.dungeon.all_entities:
            self.dungeon.all_entities.remove(self)

    def __emits_light__(self):
        return True
    
    def distance_to(self, entity):
        return abs(self.x - entity.x) + abs(self.y - entity.y)

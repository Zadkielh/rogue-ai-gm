from collections import deque
import pygame
from config import TILE_SIZE_X, TILE_SIZE_Y

class Entity(pygame.sprite.Sprite):
    def __init__(self, tile_x, tile_y, width, height, color, dungeon):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)

        self.x = float(tile_x)
        self.y = float(tile_y)

        self.rect = self.image.get_rect(topleft=(int(self.x * TILE_SIZE_X), int(self.y * TILE_SIZE_Y)))
        self.dungeon = dungeon
        self.tried_relocating = False

        self.collide = True

    def move(self, dx, dy):
        if dx == 0 and dy == 0:
            return

        old_x, old_y = self.x, self.y

        new_x = self.x + dx
        new_y = self.y + dy

        if new_x < 1:
            target_x = self.dungeon.width - 2
            if not self.dungeon.is_blocked_tile(target_x, int(new_y)):
                new_x = target_x
            else:
                new_x = old_x

        elif new_x >= self.dungeon.width - 1:
            target_x = 1
            if not self.dungeon.is_blocked_tile(target_x, int(new_y)):
                new_x = target_x
            else:
                new_x = old_x

        if new_y < 1:
            target_y = self.dungeon.height - 2
            if not self.dungeon.is_blocked_tile(int(new_x), target_y):
                new_y = target_y
            else:
                new_y = old_y
        elif new_y >= self.dungeon.height - 1:
            target_y = 1
            if not self.dungeon.is_blocked_tile(int(new_x), target_y):
                new_y = target_y
            else:
                new_y = old_y

        self.x, self.y = new_x, new_y
        self.rect.topleft = (self.x * TILE_SIZE_X, self.y * TILE_SIZE_Y)

        if self.dungeon.check_collision(self):
            self.x = old_x
            self.y = old_y
            self.rect.topleft = (self.x * TILE_SIZE_X, self.y * TILE_SIZE_Y)

        if self.check_entity_collision():
            self.x = old_x
            self.y = old_y
            self.rect.topleft = (self.x * TILE_SIZE_X, self.y * TILE_SIZE_Y)

    def check_entity_collision(self):
        for ent in self.dungeon.all_entities:
            if ent is not self:
                if ent.collide:
                    if self.rect.colliderect(ent.rect):
                        return True
        return False
    
    def update(self):
        int_x, int_y = int(self.x), int(self.y)
        if self.dungeon.is_blocked_tile(int_x, int_y) and not self.tried_relocating:
            self.tried_relocating = True
            self.move_to_nearest_unblocked_tile()

    def move_to_nearest_unblocked_tile(self):
        visited = set()
        queue = deque([(int(self.x), int(self.y))])
        found_tile = False

        while queue:
            cx, cy = queue.popleft()
            if not self.dungeon.is_blocked_tile(cx, cy):
                self.x, self.y = float(cx), float(cy)
                self.rect.topleft = (int(self.x * TILE_SIZE_X), int(self.y * TILE_SIZE_Y))
                found_tile = True
                break

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited and 0 <= nx < self.dungeon.width and 0 <= ny < self.dungeon.height:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        if not found_tile:
            print("Warning: No free tile found for entity to relocate to.")

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def __collide__(self):
        return self.collide


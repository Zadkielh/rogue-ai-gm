import pygame
import math
from config import *
from core.objects.entity import Entity
from core.objects.projectile import Projectile
from collections import deque

class Player(Entity):
    def __init__(self, dungeon, x, y):
        super().__init__(x, y, TILE_SIZE_X, TILE_SIZE_Y, (255, 255, 255), dungeon)
        self.speed = 0.05

        self.afterimages = deque()  
        self.afterimage_max = 5 
        self.afterimage_delay = 3
        self.frame_count = 0

        self.light_radius = 7

        self.direction = 0
        self.health = 20
        self.defense = 0

        self.level = 1
        self.xp = 0
        self.kills = 0

        self.cooldown_base = 1000
        self.__cooldown = 0
        self.cooldown = self.cooldown_base

        self.current_health = self.health

        self.attack_area = 1
        self.damage = 3
        self.weapon_type = "ranged"

        self.equipped_weapon = None
        self.equipped_armor = None

    def equip_item(self, item):
        if not hasattr(item, 'type'):
            print("Item has no type attribute, cannot equip.")
            return False

        if item.type == 'weapon':
            if self.equipped_weapon is not None:
                self.drop_item(self.equipped_weapon)
                self.equipped_weapon = None

            self.equipped_weapon = item
            item.equip(self)
            print(f"Equipped weapon: {item.name}")
            return True

        elif item.type == 'armor':
            if self.equipped_armor is not None:
                self.drop_item(self.equipped_armor)
                self.equipped_armor = None

            self.equipped_armor = item
            item.equip(self)
            print(f"Equipped armor: {item.name}")
            return True
        else:
            print("Item type not recognized, cannot equip.")
            return False


    def drop_item(self, item):
        drop_x, drop_y = self.find_nearby_free_tile(int(self.x), int(self.y))
        if drop_x is not None and drop_y is not None:
            item.x = drop_x
            item.y = drop_y
            item.rect.topleft = (int(drop_x * TILE_SIZE_X), int(drop_y * TILE_SIZE_Y))
            if item not in self.dungeon.all_entities:
                self.dungeon.all_entities.append(item)
            print(f"Dropped {item.name} at ({drop_x}, {drop_y})")
        else:
            print(f"No free tile found to drop {item.name}. Discarding it.")


    def find_nearby_free_tile(self, start_x, start_y, max_distance=5):
        for dist in range(1, max_distance+1):
            for dx in range(-dist, dist+1):
                for dy in range(-dist, dist+1):
                    nx = start_x + dx
                    ny = start_y + dy
                    # Check bounds
                    if 0 <= nx < self.dungeon.width and 0 <= ny < self.dungeon.height:
                        if not self.dungeon.is_blocked_tile(nx, ny) and not self.is_tile_occupied(nx, ny):
                            return nx, ny
        return None, None


    def is_tile_occupied(self, tile_x, tile_y):
        for ent in self.dungeon.all_entities:
            if int(ent.x) == tile_x and int(ent.y) == tile_y:
                return True
        return False

        
    def level_up(self):
        if self.level >= 10:
            print("Max level reached.")
            return
        
        self.level += 1
        self.health += 5
        self.damage += 2
        self.defense += 1
        self.cooldown_base -= 50
        self.cooldown = self.cooldown_base
        self.current_health = self.health
        print(f"Leveled up! New level: {self.level}")

    def take_damage(self, amount, owner):
        print(amount, self.defense)
        self.current_health -= max(amount - self.defense, 0)
        if self.current_health <= 0:
            self.die()

    def update(self):
        super().update()

        if self.xp >= self.level * 10 and self.level < 10:
            self.level_up()
        self.frame_count += 1
        if self.frame_count >= self.afterimage_delay:
            self.add_afterimage()
            self.frame_count = 0

        self.update_afterimages()

        # Handle movement
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

        if dx != 0 or dy != 0:
            angle_radians = math.atan2(dy, dx)  # dy first, dx second
            angle_degrees = math.degrees(angle_radians)

            if angle_degrees < 0:
                angle_degrees += 360

            self.direction = angle_degrees

        if keys[pygame.K_SPACE]:
            cur_time = pygame.time.get_ticks()
            if self.__cooldown <= cur_time:
                self.__cooldown = cur_time + self.cooldown
                if self.weapon_type == "ranged":
                    self.attack_arrow()
                elif self.weapon_type == "melee":
                    self.attack_arc()
                

        self.move(dx, dy)

    def add_afterimage(self):
        afterimage_pos = self.rect.topleft
        self.afterimages.append([afterimage_pos, 255])

        if len(self.afterimages) > self.afterimage_max:
            self.afterimages.popleft()

    def update_afterimages(self):
        for afterimage in self.afterimages:
            afterimage[1] -= 25
        self.afterimages = deque([img for img in self.afterimages if img[1] > 0])

    def draw(self, screen, camera):
        for afterimage_pos, opacity in self.afterimages:
            ghost_image = self.image.copy()
            ghost_image.set_alpha(opacity)
            ghost_rect = pygame.Rect(afterimage_pos, (self.rect.width, self.rect.height))
            ghost_rect.x -= camera.camera.x
            ghost_rect.y -= camera.camera.y
            screen.blit(ghost_image, ghost_rect.topleft)

        player_rect = self.rect.copy()
        player_rect.x -= camera.camera.x
        player_rect.y -= camera.camera.y
        screen.blit(self.image, player_rect)

        self.draw_health_bar(screen, player_rect)

    def attack_arrow(self):
        dx, dy = self.direction_to_vector(self.direction)
        speed = 0.5
        range_in_tiles = 30
        damage = self.damage
        proj = Projectile(self.dungeon, self.x, self.y, dx, dy, speed, range_in_tiles, damage, color=(255,255,0), owner=self)
        self.dungeon.all_entities.append(proj)

    def attack_arc(self):
        arc_spread = math.ceil(60 * self.attack_area)
        num_projectiles = math.ceil(5 * self.attack_area)
        angle_step = arc_spread / (num_projectiles - 1)
        start_angle = self.direction - (arc_spread / 2)

        range_in_tiles = 5 * self.attack_area
        damage = self.damage

        for i in range(num_projectiles):
            angle = start_angle + i * angle_step
            dx, dy = self.direction_to_vector(angle)
            proj = Projectile(self.dungeon, self.x, self.y, dx, dy, speed=0.5, range_in_tiles=range_in_tiles, damage=damage, color=(200,200,50), acceleration=-0.2, owner=self)
            self.dungeon.all_entities.append(proj)

    def direction_to_vector(self, angle_degrees):
        angle_radians = math.radians(angle_degrees)
        dx = math.cos(angle_radians)
        dy = math.sin(angle_radians)
        return dx, dy

    def draw_health_bar(self, surface, player_rect):
        bar_width = self.rect.width * 2
        bar_height = self.rect.height
        bar_offset_y = 1

        health_ratio = self.current_health / self.health
        if health_ratio < 0:
            health_ratio = 0
        elif health_ratio > 1:
            health_ratio = 1

        bar_x = player_rect.x - self.rect.width*0.35
        bar_y = player_rect.y - bar_offset_y - bar_height

        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        filled_width = int(bar_width * health_ratio)
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, filled_width, bar_height))

    def die(self):
        if self in self.dungeon.all_entities:
            self.dungeon.all_entities.remove(self)
        print(f"Game over! You reached level {self.level}.")
        exit()
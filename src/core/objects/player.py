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

        # Afterimage settings
        self.afterimages = deque()  # Store positions and transparency for afterimages
        self.afterimage_max = 5     # Maximum number of afterimages to show
        self.afterimage_delay = 3   # Delay (frames) between each afterimage creation
        self.frame_count = 0        # Used to control afterimage creation delay

        self.light_radius = 7

        self.direction = 0
        self.health = 20
        self.defense = 0

        self.level = 1
        self.xp = 0
        self.kills = 0

        self.cooldown_base = 1000  # Cooldown in milliseconds
        self.__cooldown = 0
        self.cooldown = self.cooldown_base

        self.current_health = self.health

        self.attack_area = 1
        self.damage = 3
        self.weapon_type = "ranged"

        self.equipped_weapon = None
        self.equipped_armor = None

    def equip_item(self, item):
        # Check item type and if slot is free
        if not hasattr(item, 'type'):
            print("Item has no type attribute, cannot equip.")
            return False

        if item.type == 'weapon':
            # If player already has a weapon equipped, drop it first
            if self.equipped_weapon is not None:
                self.drop_item(self.equipped_weapon)
                self.equipped_weapon = None

            self.equipped_weapon = item
            item.equip(self)
            print(f"Equipped weapon: {item.name}")
            return True

        elif item.type == 'armor':
            # If player already has armor equipped, drop it first
            if self.equipped_armor is not None:
                self.drop_item(self.equipped_armor)
                self.equipped_armor = None

            self.equipped_armor = item
            item.equip(self)
            print(f"Equipped armor: {item.name}")
            return True
        else:
            # If item has no recognized type, handle accordingly
            print("Item type not recognized, cannot equip.")
            return False


    def drop_item(self, item):
        # Try to find a nearby free tile to drop the item
        drop_x, drop_y = self.find_nearby_free_tile(int(self.x), int(self.y))
        if drop_x is not None and drop_y is not None:
            # Update item position and add to dungeon
            item.x = drop_x
            item.y = drop_y
            item.rect.topleft = (int(drop_x * TILE_SIZE_X), int(drop_y * TILE_SIZE_Y))
            if item not in self.dungeon.all_entities:
                self.dungeon.all_entities.append(item)
            print(f"Dropped {item.name} at ({drop_x}, {drop_y})")
        else:
            print(f"No free tile found to drop {item.name}. Discarding it.")
            # If no free spot found, you could either just discard the item, or handle differently.
            # For now, we do nothing, which effectively 'destroys' the item if it was equipped before.


    def find_nearby_free_tile(self, start_x, start_y, max_distance=5):
        # Check tiles in a radius around the player to find a free spot
        # For simplicity, we'll scan in a square pattern around the player
        for dist in range(1, max_distance+1):
            for dx in range(-dist, dist+1):
                for dy in range(-dist, dist+1):
                    nx = start_x + dx
                    ny = start_y + dy
                    # Check bounds
                    if 0 <= nx < self.dungeon.width and 0 <= ny < self.dungeon.height:
                        # Check if tile is not blocked and no entity occupies it
                        if not self.dungeon.is_blocked_tile(nx, ny) and not self.is_tile_occupied(nx, ny):
                            return nx, ny
        return None, None


    def is_tile_occupied(self, tile_x, tile_y):
        # Check if any entity occupies given tile coordinates
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
        # Add afterimage every few frames
        self.frame_count += 1
        if self.frame_count >= self.afterimage_delay:
            self.add_afterimage()
            self.frame_count = 0

        # Update afterimages by reducing opacity and removing fully faded ones
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

        # Determine direction only if there is movement
        # direction is in degrees, 0° = facing East, 90° = facing South, etc.
        if dx != 0 or dy != 0:
            # atan2 returns the angle in radians with 0 rad = East, and angle measured counter-clockwise.
            # In degrees:
            # East = 0°, North = -90° (or 270°), West = 180°, South = 90°.
            # We'll convert and adjust so that Up is 90°, Right is 0°, Down = 270° or -90° and so forth.
            angle_radians = math.atan2(dy, dx)  # dy first, dx second
            angle_degrees = math.degrees(angle_radians)

            # atan2(dy,dx):
            # dx>0, dy=0 => angle 0° (facing East)
            # dx=0, dy<0 => angle -90° (facing North)
            # dx<0, dy=0 => angle 180° (facing West)
            # dx=0, dy>0 => angle 90° (facing South)
            # If you prefer a different orientation, adjust here:
            # Let's keep it as standard:
            # East = 0°, North = -90°/270°, West = 180°, South = 90°

            # If you want a "gamey" orientation (e.g., Up = 90°, Right = 0°, etc.), you can just use angle_degrees as is.
            # If you want to normalize angles to 0-360:
            if angle_degrees < 0:
                angle_degrees += 360

            self.direction = angle_degrees

        # Handle attacking
        if keys[pygame.K_SPACE]:
            cur_time = pygame.time.get_ticks()
            if self.__cooldown <= cur_time:
                self.__cooldown = cur_time + self.cooldown
                if self.weapon_type == "ranged":
                    self.attack_arrow()
                elif self.weapon_type == "melee":
                    self.attack_arc()
                

        self.move(dx, dy)  # Use the move method from Entity

    def add_afterimage(self):
        """Add the current position as a new afterimage with full opacity."""
        afterimage_pos = self.rect.topleft
        self.afterimages.append([afterimage_pos, 255])  # 255 is full opacity

        # Limit the number of afterimages
        if len(self.afterimages) > self.afterimage_max:
            self.afterimages.popleft()

    def update_afterimages(self):
        """Reduce opacity of each afterimage, and remove if fully transparent."""
        for afterimage in self.afterimages:
            afterimage[1] -= 25  # Reduce opacity
        # Remove afterimages that are fully transparent
        self.afterimages = deque([img for img in self.afterimages if img[1] > 0])

    def draw(self, screen, camera):
        # Draw afterimages
        for afterimage_pos, opacity in self.afterimages:
            ghost_image = self.image.copy()
            ghost_image.set_alpha(opacity)
            ghost_rect = pygame.Rect(afterimage_pos, (self.rect.width, self.rect.height))
            ghost_rect.x -= camera.camera.x
            ghost_rect.y -= camera.camera.y
            screen.blit(ghost_image, ghost_rect.topleft)

        # Draw the player
        player_rect = self.rect.copy()
        player_rect.x -= camera.camera.x
        player_rect.y -= camera.camera.y
        screen.blit(self.image, player_rect)

        self.draw_health_bar(screen, player_rect)

    def attack_arrow(self):
        # Arrow: single projectile straight ahead with long range
        dx, dy = self.direction_to_vector(self.direction)
        speed = 0.5
        range_in_tiles = 30
        damage = self.damage
        proj = Projectile(self.dungeon, self.x, self.y, dx, dy, speed, range_in_tiles, damage, color=(255,255,0), owner=self)
        self.dungeon.all_entities.append(proj)

    def attack_arc(self):
        # Arc: multiple projectiles with different angles, shorter range
        # Let's say we fire 5 projectiles spread out over a 60-degree arc.
        # direction is in degrees for example; convert to radians for math functions.
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
        # Convert angle in degrees to a normalized direction vector (dx, dy)
        angle_radians = math.radians(angle_degrees)
        dx = math.cos(angle_radians)
        dy = math.sin(angle_radians)
        return dx, dy

    def draw_health_bar(self, surface, player_rect):
        # Bar configuration
        bar_width = self.rect.width * 2
        bar_height = self.rect.height
        bar_offset_y = 1  # How many pixels above player's sprite

        # Calculate health ratio
        health_ratio = self.current_health / self.health
        if health_ratio < 0:
            health_ratio = 0
        elif health_ratio > 1:
            health_ratio = 1

        # Position of the health bar
        bar_x = player_rect.x - self.rect.width*0.35
        bar_y = player_rect.y - bar_offset_y - bar_height

        # Draw background bar (empty)
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Draw filled portion
        filled_width = int(bar_width * health_ratio)
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, filled_width, bar_height))

    def die(self):
        if self in self.dungeon.all_entities:
            self.dungeon.all_entities.remove(self)
        print(f"Game over! You reached level {self.level}.")
        exit()
import math
import random

import pygame
from core.objects.entity import Entity
from config import TILE_SIZE_X, TILE_SIZE_Y
from core.objects.player import Player
from core.objects.projectile import Projectile
import yaml
import os

class Static(Entity):
    def __init__(self, tile_x, tile_y, dungeon, health=10, object_type="Torch", color=(0, 255, 0), area=5, damage=2, cooldown=5000, name="Unnamed Static"):
        super().__init__(tile_x, tile_y, width=TILE_SIZE_X, height=TILE_SIZE_Y, color=color, dungeon=dungeon)
        self.health = health
        self.object_type = object_type
        if self.object_type == "Torch":
            self.emits_light = True
            self.light_radius = area

        self.toggle = False
        self.effect_timer = 0
        self.timer = 0
        self.__color_timer = 0
        self.__color_toggle = False

        self.area = area
        self.damage = damage
        self.cooldown = cooldown
        self.name = name

    def update(self):
        super().update()
        if self.health <= 0:
            self.toggle = True
        
        if self.toggle:
            if self.timer is not 0 and self.timer < pygame.time.get_ticks():
                self.explode((200,200,50))
                self.toggle = False
            elif self.timer is 0:
                self.timer = pygame.time.get_ticks() + self.cooldown
                self.__color_timer = pygame.time.get_ticks() + 500
            else:
                if self.__color_timer is not 0 and self.__color_timer < pygame.time.get_ticks():
                    self.__color_timer = pygame.time.get_ticks() + 500 
                    self.__color_toggle = not self.__color_toggle
                    
                    if self.__color_toggle:
                        self.image.fill((255, 0, 0))
                    else:
                        self.image.fill((255, 255, 0))

        if self.effect_timer is not 0 and self.effect_timer < pygame.time.get_ticks():
            self.explode((255,150,50))
            self.die()
        
    def take_damage(self, amount, owner):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def interact(self, player):
        if self.object_type == "Bomb":
            self.toggle = True

    def die(self):
        if self in self.dungeon.all_entities:
            self.dungeon.all_entities.remove(self)
        print(f"{self.name} was destroyed.")

    def distance_to(self, entity):
        return abs(self.x - entity.x) + abs(self.y - entity.y)

    def get_random_direction(self):
        return random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
    
    def explode(self, color=(255, 0, 0)):
        # Arc: multiple projectiles with different angles, shorter range
        # Let's say we fire 5 projectiles spread out over a 60-degree arc.
        # direction is in degrees for example; convert to radians for math functions.
        arc_spread = 360
        num_projectiles = 30
        angle_step = arc_spread / (num_projectiles - 1)
        start_angle = 0

        range_in_tiles = self.area
        damage = self.damage

        for i in range(num_projectiles):
            angle = start_angle + i * angle_step
            dx, dy = self.direction_to_vector(angle)
            proj = Projectile(self.dungeon, self.x, self.y, dx, dy, speed=0.1, range_in_tiles=range_in_tiles, damage=damage, color=color, acceleration=-0.1, owner=self)
            self.dungeon.all_entities.append(proj)

        self.effect_timer = pygame.time.get_ticks() + 500
    
    def direction_to_vector(self, angle_degrees):
        # Convert angle in degrees to a normalized direction vector (dx, dy)
        angle_radians = math.radians(angle_degrees)
        dx = math.cos(angle_radians)
        dy = math.sin(angle_radians)
        return dx, dy


    def __emits_light__(self):
        return True if self.object_type == "Torch" else False



class StaticFactory:
    def __init__(self):
        self.static_definitions = []

    def load_static_definitions(self, file_path):
        with open(file_path, 'r') as file:
            enemy_data = yaml.safe_load(file)
            if 'statics' in enemy_data:
                self.enemy_definitions = enemy_data['statics']
            else:
                raise ValueError("No 'statics' key found in YAML.")

    def create_static(self, static_type, tile_x, tile_y, dungeon):
        for enemy_def in self.enemy_definitions:
            if enemy_def.get('type') == static_type:
                return self._create_static_from_def(enemy_def, tile_x, tile_y, dungeon)
        raise ValueError(f"Static type '{static_type}' not found in definitions.")

    def _create_static_from_def(self, enemy_def, tile_x, tile_y, dungeon):
        health = enemy_def.get('health', 10)
        class_type = enemy_def.get('class', 'Torch')
        name = enemy_def.get('name', 'Unnamed Static')
        area = enemy_def.get('area', 5)
        damage = enemy_def.get('damage', 2)
        cooldown = enemy_def.get('cooldown', 5000)
        color = tuple(enemy_def.get('color', [255, 255, 0]))

        return Static(tile_x, tile_y, dungeon, health=health, object_type=class_type, color=color, area=area, damage=damage, cooldown=cooldown, name=name)
    
static_factory = StaticFactory()
static_factory.load_static_definitions(os.path.abspath("src/config/statics.yaml"))
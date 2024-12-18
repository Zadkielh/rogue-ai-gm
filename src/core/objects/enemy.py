import random
from core.objects.entity import Entity
from config import TILE_SIZE_X, TILE_SIZE_Y
from core.objects.player import Player
import yaml
import os
import pygame

class Enemy(Entity):
    def __init__(self, tile_x, tile_y, dungeon, name="Unnamed Enemy", health=10, attack_damage=2, speed=0.01, armor=0, vision_radius=5, color=(255, 0, 0), xp=1):
        super().__init__(tile_x, tile_y, width=TILE_SIZE_X, height=TILE_SIZE_Y, color=color, dungeon=dungeon)
        self.name = name
        self.health = health
        self.attack_damage = attack_damage
        self.speed = speed
        self.armor = armor
        self.vision_radius = vision_radius
        self.emits_light = False  # Can change if needed

        self.xp = xp

        self.cooldown_base = 1000  # Cooldown in milliseconds
        self.__cooldown = 0
        self.cooldown = self.cooldown_base

    def update(self):
        super().update()
        if self.health <= 0:
            self.die()
            return

        target = self.can_see_player(self.dungeon.all_entities)
        if target:
            if self.distance_to(target) <= 1.5:
                cur_time = pygame.time.get_ticks()
                if self.__cooldown <= cur_time:
                    self.__cooldown = cur_time + self.cooldown
                    self.attack(target)
                    return

            self.chase_target(target)
        else:
            # Idle or random movement
            if random.random() < 0.01:
                return
            dx, dy = self.get_random_direction()
            self.move(dx * self.speed, dy * self.speed)

    def chase_target(self, target):
        int_x, int_y = int(self.x), int(self.y)
        target_x, target_y = int(target.x), int(target.y)

        dx = 0
        dy = 0
        if target_x < int_x:
            dx = -self.speed
        elif target_x > int_x:
            dx = self.speed

        if target_y < int_y:
            dy = -self.speed
        elif target_y > int_y:
            dy = self.speed

        self.move(dx, dy)

    def take_damage(self, amount, source):
        # Armor can reduce damage if you want, e.g.:
        # effective_damage = max(0, amount - self.armor)
        # For now, just apply damage directly:
        self.health -= amount
        if self.health <= 0:
            if isinstance(source, Player):
                source.kills += 1
                source.xp += self.xp

            self.die()

    def attack(self, target):
        if hasattr(target, 'take_damage'):
            print("Attack")
            # You could factor armor of player here too if you want
            target.take_damage(self.attack_damage, self)

    def die(self):
        if self in self.dungeon.all_entities:
            self.dungeon.all_entities.remove(self)
        print(f"{self.name} died")

    def can_see_player(self, entities):
        for entity in entities:
            if isinstance(entity, Player):
                if self.distance_to(entity) <= self.vision_radius:
                    return entity
        return False

    def distance_to(self, entity):
        return abs(self.x - entity.x) + abs(self.y - entity.y)

    def get_random_direction(self):
        return random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])



class EnemyFactory:
    def __init__(self):
        self.enemy_definitions = []

    def load_enemy_definitions(self, file_path):
        """Load enemy definitions from a YAML file."""
        with open(file_path, 'r') as file:
            enemy_data = yaml.safe_load(file)
            if 'enemies' in enemy_data:
                self.enemy_definitions = enemy_data['enemies']
            else:
                raise ValueError("No 'enemies' key found in YAML.")

    def create_enemy(self, enemy_type, tile_x, tile_y, dungeon):
        """Create an enemy instance by type at given position in the dungeon."""
        for enemy_def in self.enemy_definitions:
            if enemy_def.get('type') == enemy_type:
                return self._create_enemy_from_def(enemy_def, tile_x, tile_y, dungeon)
        raise ValueError(f"Enemy type '{enemy_type}' not found in definitions.")

    def _create_enemy_from_def(self, enemy_def, tile_x, tile_y, dungeon):
        name = enemy_def.get('name', 'Unnamed Enemy')
        health = enemy_def.get('health', 10)
        damage = enemy_def.get('damage', 2)
        speed = enemy_def.get('speed', 0.01)
        armor = enemy_def.get('armor', 0)
        vision_radius = enemy_def.get('vision_radius', 5)
        xp = enemy_def.get('xp', 1)
        color = tuple(enemy_def.get('color', [255, 0, 0]))

        return Enemy(tile_x, tile_y, dungeon, name=name, health=health, attack_damage=damage, speed=speed, armor=armor, vision_radius=vision_radius, color=color, xp=xp)
    
enemy_factory = EnemyFactory()
enemy_factory.load_enemy_definitions(os.path.abspath("src/config/enemies.yaml"))
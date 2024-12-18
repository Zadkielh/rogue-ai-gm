import yaml
import os
from config import TILE_SIZE_X, TILE_SIZE_Y
from core.objects.entity import Entity

class Item(Entity):
    def __init__(self, tile_x, tile_y, dungeon, name, description, rarity="common", color=(155, 155, 255)):
        super().__init__(tile_x, tile_y, width=TILE_SIZE_X, height=TILE_SIZE_Y, color=color, dungeon=dungeon)
        self.name = name
        self.description = description
        self.rarity = rarity
        self.emits_light = True
        self.light_radius = 1
        self.type = "item"

        self.collide = False

    def __str__(self):
        return f"{self.name} ({self.rarity})"

    def use(self, target):
        # Define a generic use method if needed
        pass

    def equip(self, target):
        pass

    def __emits_light__(self):
        return True
    
    def __type__(self):
        return self.type

    def distance_to(self, entity):
        return abs(self.x - entity.x) + abs(self.y - entity.y)
    

class Armor(Item):
    def __init__(self, tile_x, tile_y, dungeon, name, description, rarity="common", defense=0, type="armor", movespeed=1, color=(100,100,200), aclass="light"):
        # Pass tile_x, tile_y, dungeon, name, description to Item constructor
        super().__init__(tile_x, tile_y, dungeon, name, description, rarity, color)
        self.defense = defense
        self.movespeed = movespeed
        self.type = type
        self.item_class = aclass

    def equip(self, target):
        target.defense += self.defense
        target.speed = target.speed * self.movespeed

    def __item_class__(self):
        return self.item_class


class Weapon(Item):
    def __init__(self, tile_x, tile_y, dungeon, name, description, rarity="common", damage=0, type="weapon", speed=1, area=1, color=(50,50,255), wclass="melee"):
        # Pass tile_x, tile_y, dungeon, name, description to Item constructor
        super().__init__(tile_x, tile_y, dungeon, name, description, rarity, color)
        self.damage = damage
        self.speed = speed
        self.area = area
        self.type = type
        self.item_class = wclass

    def equip(self, target):
        target.damage = self.damage
        target.weapon_type = self.item_class
        target.cooldown = target.cooldown_base * self.speed
        target.attack_area = self.area

    def __item_class__(self):
        return self.item_class



class ItemFactory:
    def __init__(self):
        self.item_definitions = []

    def load_item_definitions(self, file_path):
        """Load item definitions from a YAML file."""
        with open(file_path, 'r') as file:
            item_data = yaml.safe_load(file)
            if 'items' in item_data:
                self.item_definitions = item_data['items']
            else:
                raise ValueError("No 'items' key found in YAML.")

    def create_item(self, item_name, tile_x, tile_y, dungeon):
        """Create an item instance by name at a given position in the dungeon."""
        for item_def in self.item_definitions:
            if item_def.get('name') == item_name:
                return self._create_item_from_def(item_def, tile_x, tile_y, dungeon)
        raise ValueError(f"Item '{item_name}' not found in definitions.")

    def _create_item_from_def(self, item_def, tile_x, tile_y, dungeon):
        # Common attributes
        item_type = item_def.get('type')
        name = item_def.get('name', 'Unknown Item')
        description = item_def.get('description', 'No description')
        rarity = item_def.get('rarity', 'common')

        # Different item types have different attributes
        if item_type == 'weapon':
            damage = item_def.get('damage', 0)
            wtype = item_def.get('type', 'weapon')
            speed = item_def.get('speed', 1)
            area = item_def.get('area', 1)
            wclass = item_def.get('class', 'melee')
            return Weapon(tile_x, tile_y, dungeon, name, description, rarity, damage, wtype, speed, area, wclass=wclass)
        elif item_type == 'armor':
            defense = item_def.get('defense', 0)
            atype = item_def.get('type', 'armor')
            movespeed = item_def.get('movespeed', 1)
            aclass = item_def.get('class', 'light')
            return Armor(tile_x, tile_y, dungeon, name, description, rarity, defense, atype, movespeed, aclass=aclass)
        else:
            # Generic item
            return Item(tile_x, tile_y, dungeon, name, description, rarity)

# Example usage (assuming you have items.yaml):
item_factory = ItemFactory()
item_factory.load_item_definitions(os.path.abspath("src/config/items.yaml"))

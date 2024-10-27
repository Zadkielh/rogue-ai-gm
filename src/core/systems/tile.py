import pygame

from config import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type, color):
        super().__init__()  # Initialize the Sprite superclass
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.color = color
        self.components = []

        self.image = pygame.Surface((TILE_SIZE_X, TILE_SIZE_Y))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

    def add_component(self, component):
        self.components.append(component)

    def remove_component(self, component_name):
        self.components = [comp for comp in self.components if comp.name != component_name]

    def get_component(self, component_name):
        for comp in self.components:
            if comp.name == component_name:
                return comp
        return None

    def has_component(self, component_name):
        return any(comp.name == component_name for comp in self.components)

# Tile Factory
class TileFactory:
    def __init__(self):
        self.tile_classes = {}
        self.tile_properties = {}
        self.tile_instances = []  # List to store created tile instances

    def register_tile(self, tile_name, tile_class, color):
        self.tile_classes[tile_name] = tile_class
        self.tile_properties[tile_name] = {"color": color}

    def create_tile(self, tile_type, x, y, color=(160, 32, 240)):
        if tile_type in self.tile_classes:
            color = self.tile_properties[tile_type]["color"]
            new_tile = self.tile_classes[tile_type](x, y, tile_type, color)
            self.tile_instances.append(new_tile)  # Store the instance
            return self.tile_classes[tile_type](x, y, tile_type, color)
        else:
            raise ValueError(f"Tile type '{tile_type}' is not registered.")
    
    def get_all_instances(self):
        """Return all created tile instances."""
        return self.tile_instances

# Function to inject new code
def inject_tile_class(code_str):
    # Create a temporary dictionary for local namespace
    local_namespace = {}
    try:
        # Execute the provided code
        exec(code_str, globals(), local_namespace)

        # Check if a class derived from Tile is in the local namespace
        for name, obj in local_namespace.items():
            if isinstance(obj, type) and issubclass(obj, Tile):
                # Get the tile type from the class (assuming it's the lowercase of the class name or tile_type attribute)
                tile_type = obj(x=0, y=0).tile_type
                factory.register_tile(tile_type, obj, obj(x=0, y=0).color)
                print(f"Registered new tile class: {tile_type}")
    except Exception as e:
        print(f"Error during code injection: {e}")

# Example of code to inject
new_tile_code = """
class WaterTile(Tile):
    def __init__(self, x, y, tile_type="water", color=(0,0,255)):
        super().__init__(x, y, "water", (0, 0, 255))  # Blue color for water
"""

# Creating a TileFactory instance
factory = TileFactory()
factory.register_tile("floor", lambda x, y, tile_type, color: Tile(x, y, tile_type, color), (100, 100, 100))  # Gray color for floor
factory.register_tile("wall", lambda x, y, tile_type, color: Tile(x, y, tile_type, color), (255, 0, 0))  # Red color for wall

# Inject the new class
inject_tile_class(new_tile_code)

# Create a WaterTile instance through the factory
try:
    water_tile = factory.create_tile("water", 5, 5, (0, 0, 255))
    print(f"Successfully created tile of type: {water_tile.tile_type}")
except ValueError as e:
    print(e)
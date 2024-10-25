class Tile:
    def __init__(self, x, y, tile_type, color):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.color = color
        self.components = []

    def add_component(self, component):
        self.components.append(component)

# Tile Factory
class TileFactory:
    def __init__(self):
        self.tile_classes = {
            "floor": Tile,
            "wall": Tile
        }

    def register_tile(self, tile_name, tile_class):
        self.tile_classes[tile_name] = tile_class

    def create_tile(self, tile_type, x, y):
        if tile_type in self.tile_classes:
            return self.tile_classes[tile_type](x, y, tile_type)
        else:
            raise ValueError(f"Tile type '{tile_type}' is not registered.")

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
                # Register the new tile class with the TileFactory
                factory.register_tile(name.lower(), obj)
                print(f"Registered new tile class: {name}")
    except Exception as e:
        print(f"Error during code injection: {e}")

# Example of code to inject
new_tile_code = """
class WaterTile(Tile):
    def __init__(self, x, y):
        super().__init__(x, y, "water", (0, 0, 255))  # Blue color for water
        self.add_component(Component("slippery", {"effect": "slow_down"}))
"""

# Creating a TileFactory instance
factory = TileFactory()

# Inject the new class
inject_tile_class(new_tile_code)

# Create a WaterTile instance through the factory
try:
    water_tile = factory.create_tile("water", 5, 5, (0, 0, 255))
    print(f"Successfully created tile of type: {water_tile.tile_type}")
except ValueError as e:
    print(e)

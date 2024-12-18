import os
from core.systems.tile import TileFactory

def load_resources():
    factory = TileFactory()
    factory.load_tile_definitions(os.path.abspath("src/config/tiles.yaml"))
    return factory

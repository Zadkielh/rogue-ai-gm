# src/main.py
import pygame
import sys
from core.game import Game
from src.core.systems.camera import Camera
from src.core.systems.dungeon import Dungeon
from src.core.objects.player import Player

from config import *

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AI Dungeon Master")
    clock = pygame.time.Clock()

    # Define the number of tiles to be visible in each direction
    view_distance = VIEW_ZONE*2  # Number of tiles visible

    # Calculate virtual screen dimensions based on view_distance
    virtual_width = view_distance * TILE_SIZE_X
    virtual_height = view_distance * TILE_SIZE_Y
    virtual_screen = pygame.Surface((virtual_width, virtual_height))

    # Game objects
    dungeon = Dungeon()  
    player = Player(dungeon)  
    camera = Camera(view_distance, dungeon.width // TILE_SIZE_X, dungeon.height // TILE_SIZE_Y)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.update()  # Update player logic
        camera.update(player)  # Update camera based on player position

        # Clear virtual screen
        virtual_screen.fill((0, 0, 0))  

        # Draw all game elements onto the virtual screen
        dungeon.draw(virtual_screen, camera)  # Draw the dungeon with camera offset
        virtual_screen.blit(player.image, camera.apply(player))  # Draw player with camera offset

        # Scale virtual screen to actual screen size
        scaled_surface = pygame.transform.scale(virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_surface, (0, 0))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate (FPS)
        clock.tick(MAX_FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

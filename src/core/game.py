# src/core/game.py
import pygame
from src.core.objects.player import Player

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player()

    def update(self):
        # Update the player and other game elements
        self.player.update()

    def draw(self):
        # Draw game elements
        self.player.draw(self.screen)


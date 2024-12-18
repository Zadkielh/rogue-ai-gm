import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, LIGHT_RADIUS, TILE_SIZE_X, TILE_SIZE_Y

class Renderer:
    def __init__(self, screen, camera):
        self.screen = screen
        self.camera = camera

    def render(self, dungeon, player, virtual_screen, message_text=None, message_start_time=0, message_duration=5000):

        def draw_floor_message(surface, message, start_time, duration):
            # Calculate how long since message started
            elapsed = pygame.time.get_ticks() - start_time
            if elapsed > duration:
                return  # More than 5 seconds have passed, no message

            # Calculate alpha (fade out)
            # At 0 ms -> alpha = 255 full
            # at duration ms -> alpha = 0
            alpha_ratio = 1 - (elapsed / duration)
            alpha = int(255 * alpha_ratio)

            font = pygame.font.Font(None, 24)
            text_surf = font.render(message, True, (255, 255, 255))
            # To apply alpha, convert the rendered text to a surface with alpha
            #text_surf = text_surf.convert_alpha()
            #text_surf.set_alpha(alpha)

            # Center on the screen
            text_rect = text_surf.get_rect(center=(surface.get_width()//2, surface.get_height()//2 - 50))
            surface.blit(text_surf, text_rect)

        # Clear virtual screen
        virtual_screen.fill((0, 0, 0))

        light_sources = []
        # Player tile position:
        light_sources.append(player)

        # If any other entities emit light:
        for ent in dungeon.all_entities:
            if hasattr(ent, 'emits_light') and ent.emits_light:
                light_sources.append(ent)

        # Determine which tiles are visible based on the camera and view zone
        # Convert camera pixel coordinates to tile coordinates
        start_tile_x = self.camera.camera.x // TILE_SIZE_X
        start_tile_y = self.camera.camera.y // TILE_SIZE_Y

        # The camera viewport_width and viewport_height (in tiles) should match your view_distance
        # If camera.viewport_width or viewport_height are equal to the view_distance, use them directly.
        # Otherwise, calculate them from your virtual screen size:
        viewport_tiles_x = virtual_screen.get_width() // TILE_SIZE_X
        viewport_tiles_y = virtual_screen.get_height() // TILE_SIZE_Y

        # Loop only through visible tiles
        for ty in range(start_tile_y, start_tile_y + viewport_tiles_y + 1):
            for tx in range(start_tile_x, start_tile_x + viewport_tiles_x + 1):
                # Check boundaries
                if 0 <= tx < dungeon.width and 0 <= ty < dungeon.height:
                    tile = dungeon.grid[ty][tx]
                    if tile:  # Ensure tile is not None
                        brightness = self.get_tile_brightness(tile.tile_x, tile.tile_y, light_sources)
                        tile_pos = self.camera.apply(tile)
                        virtual_screen.blit(tile.image, tile_pos)

                        # Apply dimming overlay if needed
                        if brightness < 1.0:
                            alpha = int((1.0 - brightness) * 255)
                            dim_surface = pygame.Surface((TILE_SIZE_X, TILE_SIZE_Y))
                            dim_surface.fill((0,0,0))
                            dim_surface.set_alpha(alpha)
                            virtual_screen.blit(dim_surface, tile_pos)

        for entity in dungeon.all_entities:
            if entity == player:
                continue

            # Convert entity positions to integers for indexing
            int_x = int(entity.x)
            int_y = int(entity.y)

            # Check if entity is within the camera viewport area
            if (start_tile_y <= int_y <= start_tile_y + viewport_tiles_y and
                start_tile_x <= int_x <= start_tile_x + viewport_tiles_x):

                brightness = self.get_tile_brightness(int_x, int_y, light_sources)

                # Draw the entity at its camera-adjusted position
                entity_pos = self.camera.apply(entity)
                virtual_screen.blit(entity.image, entity_pos)

                # If brightness < 1.0, apply a dimming overlay
                if brightness < 1.0:
                    alpha = int((1.0 - brightness) * 255)
                    dim_surface = pygame.Surface((entity.rect.width, entity.rect.height))
                    dim_surface.fill((0,0,0))
                    dim_surface.set_alpha(alpha)
                    virtual_screen.blit(dim_surface, entity_pos)

        # Draw the player last or handle through entities if player is in all_entities
        player.draw(virtual_screen, self.camera)

        if message_text:
            draw_floor_message(virtual_screen, message_text, message_start_time, message_duration)

        # Scale and blit to the main screen
        scaled_surface = pygame.transform.scale(virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()


    def get_tile_brightness(self, tile_x, tile_y, light_sources):

        # light_sources is a list of (lx, ly) tile coordinates of sources
        brightness = 0.0
        for light in light_sources:
            (lx, ly) = light.x, light.y
            dx = tile_x - lx
            dy = tile_y - ly
            dist = abs(dx) + abs(dy)  # Using Manhattan distance for simplicity, or use Euclidean

            # Compute brightness from this source
            if dist <= light.light_radius:
                source_brightness = 1.0
            else:
                # Steps beyond LIGHT_RADIUS
                steps_beyond = dist - light.light_radius
                if steps_beyond >= 4:
                    source_brightness = 0.0
                else:
                    # Decrease brightness by 0.25 per step
                    source_brightness = 1.0 - (0.25 * steps_beyond)

            # Combine brightness - example: take the max
            # (Alternatively, sum and clamp at 1.0)
            brightness = max(brightness, source_brightness)

        return brightness


    
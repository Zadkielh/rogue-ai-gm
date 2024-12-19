import pygame
import sys
import random
from core.systems.camera import Camera
from core.systems.dungeon import Dungeon
from core.systems.resource_manager import load_resources
from core.systems.renderer import Renderer
from core.objects.player import Player
from core.objects.stairs import Stairs
from core.objects.item import Item
from core.objects.statics import Static
from config import *
from ai.game_director import generate_yaml
import threading
import time
from core.objects.enemy import Enemy

result_lock = threading.Lock()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AI Dungeon Master")
    clock = pygame.time.Clock()

    factory = load_resources()

    # Setup the camera/view
    view_distance = VIEW_ZONE * 2  # tiles visible in each direction
    virtual_width = view_distance * TILE_SIZE_X
    virtual_height = view_distance * TILE_SIZE_Y
    virtual_screen = pygame.Surface((virtual_width, virtual_height))
    global renderer
    renderer = Renderer(screen, None)

    game_state = "loading"
    result_container = {}

    threading.Thread(target=request_gpt_data_async, args=(1, 1, 0, 20, "None", result_container), daemon=True).start()

    current_floor = 1

    message_text = ""
    message_start_time = 0
    message_duration = 5000  # 5 seconds in milliseconds

    def show_floor_message(floor_number, name):
        nonlocal message_text, message_start_time
        message_text = f"{name} - Floor {floor_number}"
        message_start_time = pygame.time.get_ticks()

    def create_floor(rooms, room_min_size, room_max_size, player=None):
        dungeon = Dungeon(rooms, room_min_size, room_max_size)
        spawn_x, spawn_y = dungeon.find_spawn_point()
        if player:
            player.x = spawn_x
            player.y = spawn_y
            player.dungeon = dungeon
            player.kills = 0
        else:
            player = Player(dungeon, spawn_x, spawn_y)
        camera = Camera(view_distance, dungeon.width, dungeon.height)
        dungeon.all_entities.append(player)
        renderer.camera = camera

        show_floor_message(current_floor, dungeon.name)

        return dungeon, player, camera

    rooms = random.randint(5, 10)
    room_min_size = random.randint(5, 20)
    room_max_size = room_min_size + random.randint(5, 20)

    dungeon = None
    player = None
    camera = None

    running = True
    while running:
        pygame.event.pump()

        if game_state == "loading":
                if "data" in result_container:
                    with result_lock:
                        dungeon, player, camera = create_floor(rooms, room_min_size, room_max_size, player)

                        for ent in dungeon.all_entities:
                            if isinstance(ent, Enemy):
                                while ent.distance_to(player) < 10:
                                    x, y = dungeon.get_random_spawn_point()
                                    ent.x = x
                                    ent.y = y

                        game_state = "playing"
                else:
                    virtual_screen.fill((0, 0, 0))
                    font = pygame.font.Font(None, 36)
                    text = font.render("Loading...", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(virtual_width // 2, virtual_height // 2))
                    virtual_screen.blit(text, text_rect)
                    scaled_surface = pygame.transform.scale(virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    screen.blit(scaled_surface, (0, 0))
                    pygame.display.flip()
                    clock.tick(60)
                    continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update entities and camera
        player.update()
        camera.update(player)

        # Check for stairs collision
        for ent in dungeon.all_entities:
            if isinstance(ent, Player):
                continue

            if ent.distance_to(player) < 30:
                if isinstance(ent, Stairs) and ent.rect.colliderect(player.rect):
                    print("Reached stairs! Next floor is: ", current_floor + 1)

                    game_state = "loading"
                    result_container = {}
                    threading.Thread(target=request_gpt_data_async, args=(current_floor + 1, player.level, player.kills, player.current_health, dungeon.theme, result_container), daemon=True).start()
                    current_floor += 1
                    
                if isinstance(ent, Item):
                    if ent.rect.colliderect(player.rect):
                        if player.equip_item(ent):
                            dungeon.all_entities.remove(ent)

                if isinstance(ent, Static):
                    if ent.distance_to(player) < 3:
                        if random.random() < 0.01:
                            ent.interact(player)
                    
                ent.update()

        renderer.render(dungeon, player, virtual_screen, message_text, message_start_time, message_duration)
        clock.tick(60)

    pygame.quit()
    sys.exit()

def request_gpt_data_async(floor, level, kills, health, theme, result_container):
    result = generate_yaml(floor, level, kills, health, theme)
    result_container["data"] = result

if __name__ == "__main__":
    main()
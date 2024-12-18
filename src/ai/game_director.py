from openai import OpenAI
from core.systems.tile import *
from core.systems.dungeon import Dungeon
import re
import random
import sys

from core.systems.tile import factory
from core.objects.enemy import enemy_factory
from core.objects.item import item_factory
from core.objects.statics import static_factory

# Initialize the OpenAI API key (replace with your actual API key)
api_key = ""
client = OpenAI(
    # This is the default and can be omitted
    api_key=api_key,
)


# Function to ask the AI to generate a new tile class
def generate_yaml(floor, level, kills, health, theme="None"):
    def request_yaml():
      prompt = f"""
You are helping me generate YAML configuration files for a tile-based roguelike game. I have a few categories of data to define: items, enemies, tiles and dungeon. Each category should produce a separate YAML file with a top-level key (e.g., "items", "enemies", "tiles") and a list of entries under it.

**Items:**
- Each item has:
  - type: one of ["weapon", "armor"]
  - name: string
  - description: string
  - rarity: one of ["common", "uncommon", "rare", "epic"]
  - damage: int (default 2)
  - class: one of ["melee", "ranged"]
  - speed: float (default 1) is a multiplier
  - area: float (default 1) is a multiplier
  - amount: int 

**Enemies:**
- Each enemy has:
  - type: string (identifier like "zombie", "skeleton")
  - name: string
  - health: int (default 10)
  - damage: int (default 1)
  - speed: float (default 0.05) (range 0.01-0.1)
  - armor: int (default 0)
  - vision_radius: int (default 5)
  - color: [R, G, B] array of ints
  - xp: int (default 2)
  - amount: int

**Tiles:**
- Each tile has:
  - name: string
  - color: [R, G, B]
  - collide: bool
  - wall: bool
  - rarity: int (default 50) is a weight

**Statics:**
- Each static has:
  - type: one of ["torch", "bomb"]
  - name: string
  - health: int (default 10)
  - class: one of ["Torch", "Bomb"]
  - area: int (default 3)
  - damage: int (default 2)
  - cooldown: int (default 5000)
  - color: [R, G, B]
  - amount: int

**Dungeon:**
- Each dungeon has:
  - name: string
  - rooms: int (default 5)
  - room_min_size: int (default 5)
  - room_max_size: int (default 10)
  - theme: string (Cave, Dungeon, Castle, etc.)
  - width: int (default 120)
  - height: int (default 80)
  - wiggly: float (default 0.2)

I want you to produce three separate YAML outputs, one for each category (items.yaml, enemies.yaml, tiles.yaml). Use realistic fantasy-themed items, enemies, and tiles. For items, produce a number of items (a mix of weapons and armor), for enemies, produce a number of enemies, and for tiles produce any number of different tiles.
The number of items, enemies, and tiles is up to you, and should be based on how difficult and varied you want the game to be. 
You should base the difficulty on the floor, level, kills, and health of the player.
Lower health would suggest the player struggled on the previous floor, and should be given only slightly more difficult enemies.
Higher kills would suggest the player is more experienced, and should be given more difficult enemies.
Higher level would suggest the player is more powerful, and should be given more difficult enemies.
As floor level increases, go more wild with the numbers on modifiers like damage, area, cooldown.
Keep within the ranges for modifiers that note a range.

Player Health: {health}
Player Kills: {kills}
Player Floor: {floor}
Player Level: {level}

The number of tiles should be based on the size of the dungeon and the number of rooms.
The room sizes should be based on the dungeon size and the theme of the dungeon.
The theme of the dungeon should be similar to the previus dungeons if the player is coming from a previous floor.
Tile Colors should be distinct between walls and other tiles, so that walls are easily distinguishable.
Tiles should be generated with a strong theme connection, and should be purely decorative in nature.
Floor tiles should be similar in color to each other. 
Wiggly is how wiggly the corridors are, with 0 being straight and 1 being very wiggly.

Floor 1 should be low fantasy, and it should increase in fantasy as the player progresses.

Make sure enemies have colors that stand out from the tiles.

Last Theme: {theme}

Please respond with five separate YAML documents in one response, in the following order:

1. items.yaml
2. enemies.yaml
3. tiles.yaml
4. statics.yaml
5. dungeon.yaml

Do not include any extra commentary, just the YAML contents.

      """


      response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
              {"role": "system", "content": "You are a balanced dungeon master, giving your players a fun experience."},
              {"role": "user", "content": prompt}
          ],
          temperature=0.7
      )
      code = response.choices[0].message.content

      # Clean up the response
      cleaned_code = re.sub(r"```yaml|```|\*", "", code).strip()
      print(cleaned_code)
      return cleaned_code

    for attempt in range(2):
        try:
            print(f"Attempt {attempt + 1} to generate YAML")
            cleaned_code = request_yaml()
            data = yaml.safe_load(cleaned_code)

            items_data = {"items": data["items"]}
            enemies_data = {"enemies": data["enemies"]}
            tiles_data = {"tiles": data["tiles"]}
            statics_data = {"statics": data["statics"]}
            dungeon_data = {"dungeon": data["dungeon"]}

            # Write YAML files
            with open("items.yaml", "w") as file:
                yaml.safe_dump(items_data, file)

            with open("enemies.yaml", "w") as file:
                yaml.safe_dump(enemies_data, file)

            with open("tiles.yaml", "w") as file:
                yaml.safe_dump(tiles_data, file)

            with open("statics.yaml", "w") as file:
                yaml.safe_dump(statics_data, file)

            with open("dungeon.yaml", "w") as file:
                yaml.safe_dump(dungeon_data, file)

            print("Files generated successfully!")

            # Load factories
            factory.load_tile_definitions("tiles.yaml")
            enemy_factory.load_enemy_definitions("enemies.yaml")
            item_factory.load_item_definitions("items.yaml")
            static_factory.load_static_definitions("statics.yaml")

            print("Factories loaded successfully!")
            return  # Exit function on success

        except Exception as e:
            print(f"Error during YAML generation: {e}")

    # If we reach here, all attempts failed
    print("Failed to generate YAML after 2 attempts. Exiting program.")
    pygame.quit()
    sys.exit()


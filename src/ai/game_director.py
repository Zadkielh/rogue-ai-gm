from openai import OpenAI
from core.systems.tile import *
from core.systems.dungeon import Dungeon
import re
import random

# Initialize the OpenAI API key (replace with your actual API key)
api_key = ""
client = OpenAI(
    # This is the default and can be omitted
    api_key=api_key,
)


# Function to ask the AI to generate a new tile class
def generate_tile_class():
    prompt = f"""
    Create a new Python class for a tile type in a game. 
    The class should:
    - Pick a random name for a tile, such as one of the following: "GrassTile", "WaterTile", "FireTile", "StoneTile", "SandTile", "LavaTile", "IceTile".
    - Inherit from the Tile class.
    - Have a color in RGB format that you select.
    - Have x, y coordinates between 2 and 38 that you select.

    **Important**:
    - Only generate the class code.
    - Do not add any import statements.
    - Do not add new methods, libraries, or anything beyond the requested.
    - Only replace the necessary values in the provided example.
    - No extra lines or modifications beyond the prompt.

    Example:
    class WaterTile(Tile):
        def __init__(self, x, y, tile_type="water", color=(0,0,255)):
            super().__init__(x, y, "water", (0, 0, 255))  # Blue color for water
    """


    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates code snippets."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7
    )
    code = response.choices[0].message.content

    # Clean up the response
    cleaned_code = re.sub(r"```python|```|\*", "", code).strip()
    print(cleaned_code)
    return cleaned_code

def inject_and_update_dungeon(dungeon):
    # Generate new tile code
    tile_code = generate_tile_class()

    # Inject the new tile code
    inject_tile_class(tile_code)

    tile_name_match = re.search(r'class (\w+Tile)\(Tile\):', tile_code)
    init_params_match = re.search(r'def __init__\(self, x, y, tile_type="(\w+)", color=(\(\d+,\s*\d+,\s*\d+\))\)', tile_code)

    if tile_name_match and init_params_match:
        tile_type = init_params_match.group(1)  # Extract the tile type (e.g., "water")
        color = eval(init_params_match.group(2))  # Extract and evaluate the color (e.g., "(0, 0, 255)" -> (0, 0, 255))
        print(init_params_match.group(0))
        # Set x and y coordinates within the specified range (2 to 38)
        x, y = random.randint(2,38), random.randint(2,38)  # Example coordinates; you could randomize these within the range of 2 to 38

        # Create an instance of the newly generated tile through the factory
        try:
            new_tile = factory.create_tile(tile_type.lower(), x, y)
            print(f"Successfully created tile of type: {new_tile.tile_type}, color: {new_tile.color}")

            # Update the dungeon with the new tile type
            dungeon.alter_tile(x*TILE_SIZE_X, y*TILE_SIZE_Y, tile_type.lower())
            print(f"Tile at ({x*TILE_SIZE_X}, {y*TILE_SIZE_Y}) updated to type: {tile_type.lower()}")
        except ValueError as e:
            print(e)
    else:
        print("Failed to extract necessary details from the generated tile class.")

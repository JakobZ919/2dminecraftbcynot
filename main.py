import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
a=0
# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Terraria Clone")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Player settings
player_size = 20
player_color = (0, 0, 255)  # Blue
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_velocity_y = 0
jump_strength = 15
gravity = 1
player_speed = 5

can_jump = False

# Inventory settings
inventory_slots = 20
inventory = {i: 0 for i in range(inventory_slots)}  # 20 slots in the inventory
inventory_open = False
selected_slot = None

# World settings
tile_size = 20
chunk_size = 120
chunk_height = 250

# Load textures
grass_texture = pygame.image.load('grass.png').convert()
dirt_texture = pygame.image.load('dirt.png').convert()
stone_texture = pygame.image.load('stone.png').convert()
wood_texture = pygame.image.load('wood.png').convert()
leaves_texture = pygame.image.load('leaves.png').convert()
stone_texture = pygame.transform.scale(stone_texture, (tile_size, tile_size))
dirt_texture = pygame.transform.scale(dirt_texture, (tile_size, tile_size))
grass_texture = pygame.transform.scale(grass_texture, (tile_size, tile_size))
wood_texture = pygame.transform.scale(wood_texture, (tile_size, tile_size))
leaves_texture = pygame.transform.scale(leaves_texture, (tile_size, tile_size))

# Block types
GRASS = 0
DIRT = 1
STONE = 2
WOOD = 3
LEAVES = 4

# Block textures dictionary
block_textures = {
    GRASS: grass_texture,
    DIRT: dirt_texture,
    STONE: stone_texture,
    WOOD: wood_texture,
    LEAVES: leaves_texture,
}

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INVENTORY_COLOR = (200, 200, 200)



# Generate a single chunk of terrain
def generate_chunk(chunk_x):
    chunk = []
    a=10
    base_ground_level = chunk_height // 2
    for x in range(chunk_size):
        column = []
        a=random.randint(a-1, a+1)

        ground_level = base_ground_level +a

        for y in range(chunk_height):
            if y > ground_level:
                column.append(STONE)  # Stone block
            elif y == ground_level-5:
                column.append(GRASS)  # Grass block
            elif y <= ground_level and y >= ground_level - 4:
                column.append(DIRT)  # Dirt block
            else:
                column.append(None)  # Air
        chunk.append(column)

    # Add trees
    for x in range(2, chunk_size - 2):  # Avoid placing trees at the very edges
        if random.random() < 0.05:  # 10% chance to place a tree
            tree_height = random.randint(4, 6)
            tree_base = chunk[x].index(GRASS)
            for y in range(tree_base - 1, tree_base - 1 - tree_height, -1):
                chunk[x][y] = WOOD
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if abs(i) + abs(
                            j) <= 2 and 0 <= x + i < chunk_size and 0 <= tree_base - tree_height + j < chunk_height:
                        chunk[x + i][tree_base - tree_height + j] = LEAVES

    return chunk


# World dictionary to store chunks
world = {}


def get_chunk(chunk_x):
    if chunk_x not in world:
        world[chunk_x] = generate_chunk(chunk_x)
    return world[chunk_x]


def draw_world(offset_x, offset_y):
    start_chunk_x = (offset_x // tile_size) // chunk_size
    end_chunk_x = ((offset_x + SCREEN_WIDTH) // tile_size) // chunk_size + 1

    for chunk_x in range(start_chunk_x, end_chunk_x):
        chunk = get_chunk(chunk_x)
        for x in range(chunk_size):
            for y in range(chunk_height):
                if chunk[x][y] is not None:
                    texture = block_textures.get(chunk[x][y])
                    if texture:
                        screen.blit(texture,
                                    ((chunk_x * chunk_size + x) * tile_size - offset_x, y * tile_size - offset_y))


def place_block(world, x, y, block_type):
    chunk_x = x // chunk_size
    block_x = x % chunk_size
    chunk = get_chunk(chunk_x)
    chunk[block_x][y] = block_type


def remove_block(world, x, y):
    chunk_x = x // chunk_size
    block_x = x % chunk_size
    chunk = get_chunk(chunk_x)
    block_type = chunk[block_x][y]
    chunk[block_x][y] = None
    return block_type


# Breaking time variables
breaking = False
break_start_time = 0
break_duration = 1  # Duration in seconds to break a block

# Crafting recipes
recipes = {
    (DIRT, DIRT): STONE,  # Example: 2 DIRT -> 1 STONE
    (STONE, WOOD): GRASS,  # Example: 1 STONE + 1 WOOD -> 1 GRASS
}

# Inventory dimensions
inv_columns = 5
inv_rows = 4
slot_size = 40
inventory_surface = pygame.Surface((inv_columns * slot_size, inv_rows * slot_size))
inventory_surface.fill(INVENTORY_COLOR)


# Draw inventory slots
def draw_inventory():
    inventory_surface.fill(INVENTORY_COLOR)
    for i in range(inventory_slots):
        x = (i % inv_columns) * slot_size
        y = (i // inv_columns) * slot_size
        pygame.draw.rect(inventory_surface, BLACK, (x, y, slot_size, slot_size), 2)
        if inventory[i] > 0:
            block_type = i
            texture = block_textures.get(block_type)
            if texture:
                inventory_surface.blit(texture, (x + 5, y + 5))
            font = pygame.font.Font(None, 36)
            text = font.render(str(inventory[i]), True, BLACK)
            inventory_surface.blit(text, (x + 20, y + 20))
    screen.blit(inventory_surface, (
    SCREEN_WIDTH // 2 - inventory_surface.get_width() // 2, SCREEN_HEIGHT // 2 - inventory_surface.get_height() // 2))


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                inventory_open = not inventory_open
        if inventory_open:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if SCREEN_WIDTH // 2 - inventory_surface.get_width() // 2 <= mouse_x <= SCREEN_WIDTH // 2 + inventory_surface.get_width() // 2 and \
                        SCREEN_HEIGHT // 2 - inventory_surface.get_height() // 2 <= mouse_y <= SCREEN_HEIGHT // 2 + inventory_surface.get_height() // 2:
                    inv_x = (mouse_x - (SCREEN_WIDTH // 2 - inventory_surface.get_width() // 2)) // slot_size
                    inv_y = (mouse_y - (SCREEN_HEIGHT // 2 - inventory_surface.get_height() // 2)) // slot_size
                    slot = inv_y * inv_columns + inv_x
                    if selected_slot is None:
                        selected_slot = slot
                    else:
                        if selected_slot != slot:
                            inventory[selected_slot], inventory[slot] = inventory[slot], inventory[selected_slot]
                        selected_slot = None
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                block_x = (mouse_x + player_x - SCREEN_WIDTH // 2) // tile_size
                block_y = (mouse_y + player_y - SCREEN_HEIGHT // 2) // tile_size
                if event.button == 1:  # Left mouse button to place block
                    if inventory[DIRT] > 0:
                        place_block(world, block_x, block_y, DIRT)
                        inventory[DIRT] -= 1
                elif event.button == 3:  # Right mouse button to start breaking block
                    breaking = True
                    break_start_time = time.time()
                    block_to_break = (block_x, block_y)

    if breaking and time.time() - break_start_time >= break_duration:
        block_type = remove_block(world, block_to_break[0], block_to_break[1])
        if block_type is not None:
            inventory[block_type] += 1
        breaking = False

    # Handle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed
    if keys[pygame.K_SPACE] and can_jump:
        player_velocity_y = -jump_strength
        can_jump = False

    # Apply gravity
    player_velocity_y += gravity
    player_y += player_velocity_y

    # Collision with ground


    # Collision with blocks
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    for chunk_x in world:
        chunk = world[chunk_x]
        for x in range(chunk_size):
            for y in range(chunk_height):
                if chunk[x][y] is not None:
                    block_rect = pygame.Rect((chunk_x * chunk_size + x) * tile_size, y * tile_size, tile_size,
                                             tile_size)
                    if player_rect.colliderect(block_rect):
                        if player_velocity_y > 0:
                            player_y = block_rect.top - player_size
                            player_velocity_y = 0
                            can_jump = True
                        elif player_velocity_y < 0:
                            player_y = block_rect.bottom
                            player_velocity_y = 0

    # Drawing
    screen.fill(WHITE)  # White background
    draw_world(player_x - SCREEN_WIDTH // 2, player_y - SCREEN_HEIGHT // 2)
    pygame.draw.rect(screen, player_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, player_size, player_size))

    if inventory_open:
        draw_inventory()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

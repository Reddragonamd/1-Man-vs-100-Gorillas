import pygame
from os.path import join
from os import walk

# Game setup
WIN_WIDTH = 1280
WIN_HEIGHT = 720
FPS = 60
TILESIZE = 64

# Layers
PLAYER_LAYER = 5
ITEM_LAYER = 4
ENEMY_LAYER = 3
BLOCK_LAYER = 2
GROUND_LAYER = 1

# Player settings
PLAYER_SPEED = 5

# Enemy settings
ENEMY1_SPEED = 2
ENEMY2_SPEED = 3
ENEMY3_SPEED = 4
ENEMY4_SPEED = 5

# Colors
RED = (225, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Controls
CONTROLS = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "up": pygame.K_w,
    "down": pygame.K_s,
    "shoot": pygame.K_SPACE,
    "melee": pygame.BUTTON_LEFT,
    "resize": pygame.K_f
}
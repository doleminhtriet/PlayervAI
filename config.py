# config.py

import pygame

# Initialize Pygame (needed for font definitions)
pygame.init()

# Window and tile settings
TILE_SIZE = 50
WINDOW_WIDTH = 10 * TILE_SIZE
WINDOW_HEIGHT = 12 * TILE_SIZE
WINDOW_TITLE = "Maze Race: Player vs AI"

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)    # Player color
RED = (255, 0, 0)     # AI color
GREEN = (0, 255, 0)   # Goal color
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)

# Font settings
FONT = pygame.font.SysFont(None, 30)
WINNER_FONT = pygame.font.SysFont(None, 60)

# Maze library (can add more mazes here)
MAZE_LIBRARY = [
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # Goal at [8, 8] is reachable
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 1]
    ]
]

# Initial positions
START_POS = [1, 1]
GOAL_POS = [8, 8]

# AI Q-learning parameters
ACTIONS = ["left", "right", "up", "down"]
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 1.0
MIN_EXPLORATION_RATE = 0.01
EXPLORATION_DECAY = 0.995

# Button settings
NEXT_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 60, 100, 30)

# Frame rate
FPS = 10
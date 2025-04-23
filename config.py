# config.py
import pygame

# Initialize Pygame (needed for font definitions)
pygame.init()

# Window and tile settings
TILE_SIZE = 30
WINDOW_WIDTH = 16 * TILE_SIZE  # 480
WINDOW_HEIGHT = 18 * TILE_SIZE # 540
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
FONT = pygame.font.SysFont(None, 20)  # Smaller font for smaller tiles
WINNER_FONT = pygame.font.SysFont(None, 40)

# Maze is now generated dynamically using generator.py

# Initial positions
START_POS = [1, 1]

# AI Q-learning parameters
ACTIONS = ["left", "right", "up", "down"]
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 1.0
MIN_EXPLORATION_RATE = 0.01
EXPLORATION_DECAY = 0.995

# Button settings
NEXT_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 85, 100, 30)
BACK_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 45, 100, 30)
# Frame rate
FPS = 10
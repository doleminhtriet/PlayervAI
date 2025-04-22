# maze_race.py
from button import Button
from pygame.locals import *
import sys
import pygame
import numpy as np
import random
import time
from config import *  # Import all settings from config.py

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# Game state variables
current_maze_idx = 0
maze = MAZE_LIBRARY[current_maze_idx]
player_pos = START_POS.copy()
ai_pos = START_POS.copy()

start_time = None     # Timer starts when first move is made
elapsed_time = 0
game_over = False
winner = None         # Will store "Player" or "AI" when someone reaches green box

#  5544setup
q_table = np.zeros((10, 10, len(ACTIONS)))
episodes = 0


# Main game loop setup
show_menu = True
running = True
clock = pygame.time.Clock()
exploration_rate = EXPLORATION_RATE  # Initial value from config

# Reward function for AI
def get_reward(pos):
    """Calculate reward for AI's position"""
    if pos == GOAL_POS:  # Reaching green box gives big reward
        return 100
    elif maze[pos[1]][pos[0]] == 1:  # Hitting wall is bad
        return -10
    else:  # Regular move
        return -1

# Calculate next position based on action
def get_next_pos(pos, action):
    """Get next position based on current position and action"""
    new_pos = pos.copy()
    if action == "left" and new_pos[0] > 0:
        new_pos[0] -= 1
    elif action == "right" and new_pos[0] < 9:
        new_pos[0] += 1
    elif action == "up" and new_pos[1] > 0:
        new_pos[1] -= 1
    elif action == "down" and new_pos[1] < 9:
        new_pos[1] += 1
    return new_pos



def game_loop():
    global running
    global game_over
    global exploration_rate
    global ai_pos
    global maze
    global start_time
    global player_pos
    global current_maze_idx
    global elapsed_time
    global episodes

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            # Player movement (arrow keys)
            if not game_over and event.type == pygame.KEYDOWN:
                new_pos = player_pos.copy()
                if event.key == pygame.K_LEFT and new_pos[0] > 0:
                    new_pos[0] -= 1
                elif event.key == pygame.K_RIGHT and new_pos[0] < 9:
                    new_pos[0] += 1
                elif event.key == pygame.K_UP and new_pos[1] > 0:
                    new_pos[1] -= 1
                elif event.key == pygame.K_DOWN and new_pos[1] < 9:
                    new_pos[1] += 1
                if maze[new_pos[1]][new_pos[0]] == 0:  # Only move if not a wall
                    player_pos = new_pos
                    if start_time is None:  # Start timer on first move
                        start_time = time.time()

            # Handle "Next" button click after game over
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if NEXT_BUTTON.collidepoint(event.pos):
                    current_maze_idx = (current_maze_idx + 1) % len(MAZE_LIBRARY)
                    maze = MAZE_LIBRARY[current_maze_idx]
                    player_pos = START_POS.copy()
                    ai_pos = START_POS.copy()
                    start_time = None
                    elapsed_time = 0
                    game_over = False
                    winner = None
                    episodes += 1
                    print(f"Switched to Maze {current_maze_idx + 1}")

        # AI movement (Q-learning)
        if not game_over:
            # Choose action: explore or exploit
            if random.uniform(0, 1) < exploration_rate:
                action = random.choice(ACTIONS)
            else:
                action = ACTIONS[np.argmax(q_table[ai_pos[1]][ai_pos[0]])]

            # Update Q-table and move AI
            next_pos = get_next_pos(ai_pos, action)
            reward = get_reward(next_pos)
            old_q = q_table[ai_pos[1]][ai_pos[0]][ACTIONS.index(action)]
            next_max_q = np.max(q_table[next_pos[1]][next_pos[0]])
            new_q = old_q + LEARNING_RATE * (reward + DISCOUNT_FACTOR * next_max_q - old_q)
            q_table[ai_pos[1]][ai_pos[0]][ACTIONS.index(action)] = new_q

            if maze[next_pos[1]][next_pos[0]] == 0:  # Only move if not a wall
                ai_pos = next_pos
                if start_time is None:  # Start timer on first move
                    start_time = time.time()

            # Decay exploration rate
            exploration_rate = max(MIN_EXPLORATION_RATE, exploration_rate * EXPLORATION_DECAY)

        # Update elapsed time
        if start_time is not None and not game_over:
            elapsed_time = time.time() - start_time

        # Check for winner: First to step on green box (goal_pos) wins
        if not game_over and (player_pos == GOAL_POS or ai_pos == GOAL_POS):
            game_over = True
            winner = "Player" if player_pos == GOAL_POS else "AI"  # Whoever reaches green box first
            print(f"Episode {episodes + 1}: {winner} Wins on Maze {current_maze_idx + 1} in {elapsed_time:.2f} seconds!")

        # Draw game elements
        screen.fill(WHITE)
        for y in range(10):
            for x in range(10):
                if maze[y][x] == 1:
                    pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Draw goal (green box), player (blue), and AI (red)
        pygame.draw.rect(screen, GREEN, (GOAL_POS[0] * TILE_SIZE, GOAL_POS[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, BLUE, (player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, RED, (ai_pos[0] * TILE_SIZE, ai_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Display timer and maze number
        timer_text = FONT.render(f"Time: {elapsed_time:.2f}s", True, BLACK)
        screen.blit(timer_text, (10, WINDOW_HEIGHT - 40))
        maze_text = FONT.render(f"Maze {current_maze_idx + 1}", True, BLACK)
        screen.blit(maze_text, (10, 10))

        # Victory screen when someone wins
        if game_over:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(GRAY)
            screen.blit(overlay, (0, 0))

            # Display winner - emphasize green box as win condition
            winner_color = BLUE if winner == "Player" else RED
            winner_text = WINNER_FONT.render(f"{winner} Reached", True, winner_color)
            goal_text = FONT.render("the Green Box First!", True, GREEN)
            time_text = FONT.render(f"Time: {elapsed_time:.2f}s", True, WHITE)
            
            winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
            goal_rect = goal_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            time_rect = time_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            
            screen.blit(winner_text, winner_rect)
            screen.blit(goal_text, goal_rect)
            screen.blit(time_text, time_rect)

            # Draw Next button
            pygame.draw.rect(screen, YELLOW, NEXT_BUTTON)
            next_text = FONT.render("Next", True, BLACK)
            next_rect = next_text.get_rect(center=NEXT_BUTTON.center)
            screen.blit(next_text, next_rect)

    
        # Update display and control frame rate
        pygame.display.flip()
        clock.tick(FPS)


BG = pygame.image.load("assets/background.png")
SCREEN = pygame.display.set_mode((500,600))
def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)

def main_menu():

    #music = pygame.mixer.music.load('Audio/MenuMusic.wav')
    #pygame.mixer.music.play(-1, 0.0)
    #BGM

    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(60).render("M-AI-ZE", True, "#ffffff")
        MENU_RECT = MENU_TEXT.get_rect(center=(250, 75))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/PlayRect.png"), pos=(250, 250), 
                            text_input="PLAY", font=get_font(40), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/QuitRect.png"), pos=(250, 350), 
                            text_input="QUIT", font=get_font(40), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                   # pygame.mixer.music.stop()
                    difficulty_select() #Soon
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def difficulty_select():
   # Difficulty_music = pygame.mixer.music.load('Audio/DifficultySelectMusic.wav')
   # pygame.mixer.music.play(-1, 0.0)
   # GAMEBGM

    Difficulty_image = pygame.image.load('assets/Difficulty.png').convert()
    screen.blit(Difficulty_image,(0,0))
    
    while True:
        
        DIFFICULTY_SELECT_MOUSE_POS = pygame.mouse.get_pos()

        #SCREEN.fill("Gray")

        DIFFICULTY_SELECT_TEXT = get_font(28).render("SELECT DIFFICULTY", True, "White")
        DIFFICULTY_SELECT_RECT = DIFFICULTY_SELECT_TEXT.get_rect(center=(250, 100))
        SCREEN.blit(DIFFICULTY_SELECT_TEXT, DIFFICULTY_SELECT_RECT)

        DIFFICULTY_SELECT_BACK = Button(image=None, pos=(250, 750), 
                            text_input="BACK", font=get_font(35), base_color="Black", hovering_color="Green")

        DIFFICULTY_SELECT_BACK.changeColor(DIFFICULTY_SELECT_MOUSE_POS)
        DIFFICULTY_SELECT_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if DIFFICULTY_SELECT_BACK.checkForInput(DIFFICULTY_SELECT_MOUSE_POS):
                    main_menu()
        EASY_BUTTON = Button(image=pygame.image.load("assets/PlayRect.png"), pos=(250, 200), 
                            text_input="Easy", font=get_font(25), base_color="#d7fcd4", hovering_color="White")
        MEDIUM_BUTTON = Button(image=pygame.image.load("assets/PlayRect.png"), pos=(250, 350), 
                            text_input="Medium", font=get_font(25), base_color="#d7fcd4", hovering_color="White")
        BLACKOUT_BUTTON = Button(image=pygame.image.load("assets/PlayRect.png"), pos=(250, 500), 
                            text_input="Blackout", font=get_font(25), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(DIFFICULTY_SELECT_TEXT, DIFFICULTY_SELECT_RECT)

        for button in [EASY_BUTTON, MEDIUM_BUTTON, BLACKOUT_BUTTON]:
            button.changeColor(DIFFICULTY_SELECT_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if EASY_BUTTON.checkForInput(DIFFICULTY_SELECT_MOUSE_POS):
                    pygame.mixer.music.stop()
                    game_loop()
                if MEDIUM_BUTTON.checkForInput(DIFFICULTY_SELECT_MOUSE_POS):
                    pygame.mixer.music.stop()
                    #medium()
                if BLACKOUT_BUTTON.checkForInput(DIFFICULTY_SELECT_MOUSE_POS):
                    pygame.mixer.music.stop()
                    #blackout()
        pygame.display.update()



# Main game loop
main_menu()


# Cleanup
pygame.quit()
sys.exit()
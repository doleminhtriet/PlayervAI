# maze_race.py
from button import Button
from pygame.locals import *
import sys
import pygame
import numpy as np
import random
import time
from config import *  # Import all settings from config.py
from generator import generate_maze  # Import maze generator

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# Game state variables
maze_size = 10
maze = generate_maze(size=maze_size)
player_pos = START_POS.copy()  # [1, 1]
ai_pos = START_POS.copy()      # [1, 1]
goal_pos = [maze_size - 2, maze_size - 2]  # [8, 8] for 10x10
current_mode = "Easy"  # Default mode
start_time = None      # Timer starts when first move is made
elapsed_time = 0
game_over = False
winner = None          # Will store "Player" or "AI" when someone reaches green box
debug_mode = False

# Setup
q_table = np.zeros((maze_size, maze_size, len(ACTIONS)))
episodes = 0

# Main game loop setup
running = True
clock = pygame.time.Clock()
exploration_rate = EXPLORATION_RATE  # Initial value from config

# Reward function for AI
def get_reward(pos):
    """Calculate reward for AI's position"""
    if pos == goal_pos:  # Reaching green box gives big reward
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
    elif action == "right" and new_pos[0] < maze_size - 1:
        new_pos[0] += 1
    elif action == "up" and new_pos[1] > 0:
        new_pos[1] -= 1
    elif action == "down" and new_pos[1] < maze_size - 1:
        new_pos[1] += 1
    return new_pos

def game_loop():
    global running, game_over, exploration_rate, ai_pos, maze, start_time
    global player_pos, elapsed_time, episodes, maze_size, goal_pos, q_table, winner
    global debug_mode

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            

            #DEBUG MODE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    debug_mode = not debug_mode 
                    print(f"Debug Mode {'ON' if debug_mode else 'OFF'}")
        
            # Player movement (arrow keys)
            if not game_over and event.type == pygame.KEYDOWN:
                new_pos = player_pos.copy()
                if event.key == pygame.K_LEFT and new_pos[0] > 0:
                    new_pos[0] -= 1
                elif event.key == pygame.K_RIGHT and new_pos[0] < maze_size - 1:
                    new_pos[0] += 1
                elif event.key == pygame.K_UP and new_pos[1] > 0:
                    new_pos[1] -= 1
                elif event.key == pygame.K_DOWN and new_pos[1] < maze_size - 1:
                    new_pos[1] += 1
                if maze[new_pos[1]][new_pos[0]] == 0:  # Only move if not a wall
                    player_pos = new_pos
                    if start_time is None:  # Start timer on first move
                        start_time = time.time()

            # Handle "Next" and "Back" button click after game over
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if NEXT_BUTTON.collidepoint(event.pos):
                    maze_size = 16 if current_mode in ["Medium", "Blackout"] else 10
                    maze = generate_maze(size=maze_size)
                    player_pos = START_POS.copy()
                    ai_pos = START_POS.copy()
                    goal_pos = [maze_size - 2, maze_size - 2]
                    q_table = np.zeros((maze_size, maze_size, len(ACTIONS)))
                    start_time = None
                    elapsed_time = 0
                    game_over = False
                    winner = None
                    episodes += 1
                    print(f"Generated new {maze_size}x{maze_size} maze for Episode {episodes + 1}")
                if BACK_BUTTON.collidepoint(event.pos):
                    difficulty_select()

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
        if not game_over and (player_pos == goal_pos or ai_pos == goal_pos):
            game_over = True
            winner = "Player" if player_pos == goal_pos else "AI"
            print(f"Episode {episodes + 1}: {winner} Wins in {elapsed_time:.2f} seconds!")

        # Draw game elements
        screen.fill(WHITE)

        #Stretch out the maze if in Easy to fill screen - Alex
        bottom_margin = 60
        if current_mode == "Easy":
            draw_tile_size = min(WINDOW_WIDTH // maze_size, (WINDOW_HEIGHT - bottom_margin) // maze_size)
        else:
            draw_tile_size = TILE_SIZE



        if current_mode == "Blackout":
            # Blackout mode: render only 3x3 areas around player, AI, and goal
            for y in range(maze_size):
                for x in range(maze_size):
                    # Check if tile is within 3x3 of player, AI, or goal
                    is_visible = (
                        (abs(x - player_pos[0]) <= 1 and abs(y - player_pos[1]) <= 1) or
                        (abs(x - ai_pos[0]) <= 1 and abs(y - ai_pos[1]) <= 1) or
                        (abs(x - goal_pos[0]) <= 1 and abs(y - goal_pos[1]) <= 1)
                    )
                    if is_visible and maze[y][x] == 1:
                        pygame.draw.rect(screen, BLACK, (x * draw_tile_size, y * draw_tile_size, draw_tile_size, draw_tile_size))
                    elif not is_visible:
                        pygame.draw.rect(screen, BLACK, (x * draw_tile_size, y * draw_tile_size, draw_tile_size, draw_tile_size))
        else:
            # Normal rendering for Easy and Medium
            for y in range(maze_size):
                for x in range(maze_size):
                    if maze[y][x] == 1:
                        pygame.draw.rect(screen, BLACK, (x * draw_tile_size, y * draw_tile_size, draw_tile_size, draw_tile_size))

        # Draw goal (green box), player (blue), and AI (red)
        pygame.draw.rect(screen, GREEN, (goal_pos[0] * draw_tile_size, goal_pos[1] * draw_tile_size, draw_tile_size, draw_tile_size))
        pygame.draw.rect(screen, BLUE, (player_pos[0] * draw_tile_size, player_pos[1] * draw_tile_size, draw_tile_size, draw_tile_size))
        pygame.draw.rect(screen, RED, (ai_pos[0] * draw_tile_size, ai_pos[1] * draw_tile_size, draw_tile_size, draw_tile_size))

        # Draw border around maze - Alex
        maze_pixel_width = maze_size * draw_tile_size
        maze_pixel_height = maze_size * draw_tile_size
        pygame.draw.rect(screen, BLACK, (0, 0, maze_pixel_width, maze_pixel_height), 4)

        #Draw Debug Info when Enabled
        if debug_mode:
            #Show Player position, AI position, and Steps with episode number
            playerPos = FONT.render(f"Player: {player_pos}", True, RED)
            aiPos = FONT.render(f"AI: {ai_pos}", True, RED)
            steps = FONT.render(f"Steps (Episode {episodes+1}): {elapsed_time:.2f}s", True, RED)

            screen.blit(playerPos, (WINDOW_WIDTH - 200, 10))
            screen.blit(aiPos, (WINDOW_WIDTH - 200, 30))
            screen.blit(steps, (WINDOW_WIDTH - 200, 50))

            #Draw blue box around goal
            pygame.draw.rect(screen, BLUE, (goal_pos[0] * draw_tile_size, goal_pos[1] * draw_tile_size, draw_tile_size, draw_tile_size), 2)

        # Display timer and episode number
        timer_text = FONT.render(f"Time: {elapsed_time:.2f}s", True, BLACK)
        screen.blit(timer_text, (10, WINDOW_HEIGHT - 40))
        maze_text = FONT.render(f"Episode {episodes + 1}", True, BLACK)
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

            # Draw Back button
            pygame.draw.rect(screen, BLACK, BACK_BUTTON)
            back_text = FONT.render("Back", True, WHITE)
            back_rect = next_text.get_rect(center=BACK_BUTTON.center)
            screen.blit(back_text, back_rect)

        # Update display and control frame rate
        pygame.display.flip()
        clock.tick(FPS)

BG = pygame.image.load("assets/Background.png")
SCREEN = pygame.display.set_mode((500,600))
def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)

def main_menu():
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
                    game_rules()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def game_rules():
    while True:
        SCREEN.blit(BG, (0, 0))

        RULES_MOUSE_POS = pygame.mouse.get_pos()

        TITLE_TEXT = get_font(40).render("Game Rules", True, "#ffffff")
        TITLE_RECT = TITLE_TEXT.get_rect(center=(250, 75))

        # Text displaying rules
        rules = "You BLUE player must reach the"
        rulesCont = "GREEN goal before the RED AI!"

        RULES_TEXT = get_font(15).render(rules, True, "#ffffff")
        RULES_RECT = RULES_TEXT.get_rect(center=(250, 150))

        RULESCONT_TEXT = get_font(15).render(rulesCont, True, "#ffffff")
        RULESCONT_RECT = RULESCONT_TEXT.get_rect(center=(250, 200))

        # Continue button
        CONTINUE_BUTTON = Button(image=pygame.image.load("assets/PlayRect.png"), pos=(250, 450), 
                            text_input="continue", font=get_font(30), base_color="#d7fcd4", hovering_color="White")
        
        SCREEN.blit(TITLE_TEXT, TITLE_RECT)
        SCREEN.blit(RULES_TEXT, RULES_RECT)
        SCREEN.blit(RULESCONT_TEXT, RULESCONT_RECT)


        for button in [CONTINUE_BUTTON]:
            button.changeColor(RULES_MOUSE_POS)
            button.update(SCREEN)

        # Choices player can make
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if CONTINUE_BUTTON.checkForInput(RULES_MOUSE_POS):
                    difficulty_select()

        pygame.display.update()

def difficulty_select():
    global maze, player_pos, ai_pos, episodes, maze_size, goal_pos, q_table, current_mode, winner
    Difficulty_image = pygame.image.load('assets/Difficulty.png').convert()
    
    while True:
        SCREEN.blit(Difficulty_image, (0, 0))
        DIFFICULTY_SELECT_MOUSE_POS = pygame.mouse.get_pos()

        DIFFICULTY_SELECT_TEXT = get_font(28).render("SELECT DIFFICULTY", True, "White")
        DIFFICULTY_SELECT_RECT = DIFFICULTY_SELECT_TEXT.get_rect(center=(250, 100))
        SCREEN.blit(DIFFICULTY_SELECT_TEXT, DIFFICULTY_SELECT_RECT)

        DIFFICULTY_SELECT_BACK = Button(image=None, pos=(250, 750), 
                                       text_input="BACK", font=get_font(35), 
                                       base_color="Black", hovering_color="Green")
        EASY_BUTTON = Button(image=pygame.image.load("assets/PlayRect.png"), pos=(250, 200), 
                            text_input="Easy", font=get_font(25), base_color="#d7fcd4", hovering_color="White")
        MEDIUM_BUTTON = Button(image=pygame.image.load("assets/PlayRect.png"), pos=(250, 350), 
                              text_input="Medium", font=get_font(25), base_color="#d7fcd4", hovering_color="White")
        BLACKOUT_BUTTON = Button(image=pygame.image.load("assets/PlayRect.png"), pos=(250, 500), 
                                text_input="Blackout", font=get_font(25), base_color="#d7fcd4", hovering_color="White")

        for button in [DIFFICULTY_SELECT_BACK, EASY_BUTTON, MEDIUM_BUTTON, BLACKOUT_BUTTON]:
            button.changeColor(DIFFICULTY_SELECT_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if DIFFICULTY_SELECT_BACK.checkForInput(DIFFICULTY_SELECT_MOUSE_POS):
                    main_menu()
                if EASY_BUTTON.checkForInput(DIFFICULTY_SELECT_MOUSE_POS):
                    maze_size = 10
                    maze = generate_maze(size=maze_size)
                    player_pos = START_POS.copy()
                    ai_pos = START_POS.copy()
                    goal_pos = [maze_size - 2, maze_size - 2]
                    q_table = np.zeros((maze_size, maze_size, len(ACTIONS)))
                    episodes = 0
                    current_mode = "Easy"
                    pygame.mixer.music.stop()
                    game_loop()
                if MEDIUM_BUTTON.checkForInput(DIFFICULTY_SELECT_MOUSE_POS):
                    maze_size = 16
                    maze = generate_maze(size=maze_size)
                    player_pos = START_POS.copy()
                    ai_pos = START_POS.copy()
                    goal_pos = [maze_size - 2, maze_size - 2]
                    q_table = np.zeros((maze_size, maze_size, len(ACTIONS)))
                    episodes = 0
                    current_mode = "Medium"
                    pygame.mixer.music.stop()
                    game_loop()
                if BLACKOUT_BUTTON.checkForInput(DIFFICULTY_SELECT_MOUSE_POS):
                    maze_size = 16
                    maze = generate_maze(size=maze_size)
                    player_pos = START_POS.copy()
                    ai_pos = START_POS.copy()
                    goal_pos = [maze_size - 2, maze_size - 2]
                    q_table = np.zeros((maze_size, maze_size, len(ACTIONS)))
                    episodes = 0
                    current_mode = "Blackout"
                    pygame.mixer.music.stop()
                    game_loop()

        pygame.display.update()

# Main game loop
main_menu()

# Cleanup
pygame.quit()
sys.exit()

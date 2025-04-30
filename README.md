# PlayervAI

**Overview**

Maze Race is a Pygame-based game where players and AI agents compete to reach a green goal in a randomly generated maze. The enhanced version supports multiple players, multiple AI agents using Q-learning, and monsters as dynamic obstacles. The game offers three difficulty modes and a dynamic, engaging experience.

---

## Features

- **Q-Learning**:  
  AIs learn optimal paths with rewards:  
  - +100 for reaching the goal  
  - -50 for encountering a monster  
  - -10 for hitting a wall  
  - -1 for each move  

- **User Interface**:  
  - Main menu  
  - Difficulty selection  
  - Timer  
  - Episode counter  
  - Victory screen with Next/Back buttons  

---

## Installation

### 1. Prerequisites

- Python 3.8+  
- Pygame  
  ```bash
  pip install pygame

### 2. Clone the Repository

  ```bash
  git clone https://github.com/doleminhtriet/PlayervAI
  cd maze-race
  ```

### 3. Clone the Repository

  ```bash
  PlayervAI
  ├── __pycache__
  │   ├── button.cpython-313.pyc
  │   ├── config.cpython-313.pyc
  │   ├── generator.cpython-313.pyc
  │   └── maze_race.cpython-313.pyc
  ├── assets
  │   ├── Background.png
  │   ├── Difficulty.png
  │   ├── font.ttf
  │   ├── OptionsRect.png
  │   ├── Pixeled.ttf
  │   ├── PlayRect.png
  │   └── QuitRect.png
  ├── button.py
  ├── config.py
  ├── generator.py
  ├── maze_race.py
  └── README.md
  ```
### 4. Run the Game
  ```bash
  python maze_race.py



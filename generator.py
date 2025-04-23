import random

def generate_maze(size=10, start=(1, 1), goal=None):
    """Generate a random maze using depth-first search with backtracking."""
    # Set goal to bottom-right corner if not specified
    if goal is None:
        goal = (size - 2, size - 2)
    
    # Initialize maze with walls (1)
    maze = [[1 for _ in range(size)] for _ in range(size)]
    
    # Set start and goal as paths (0)
    maze[start[1]][start[0]] = 0
    maze[goal[1]][goal[0]] = 0
    
    def is_valid(x, y):
        """Check if (x, y) is within bounds and is a wall."""
        return 0 <= x < size and 0 <= y < size and maze[y][x] == 1
    
    def get_neighbors(x, y):
        """Get valid neighbors for carving paths, ensuring 2-cell jumps."""
        neighbors = []
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]  # Up, down, left, right
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def carve_path(x, y):
        """Recursively carve paths from (x, y)."""
        maze[y][x] = 0  # Mark current cell as path
        for nx, ny in get_neighbors(x, y):
            if maze[ny][nx] == 1:  # If neighbor is a wall
                # Carve intermediate cell (the cell between current and neighbor)
                mid_x, mid_y = (x + nx) // 2, (y + ny) // 2
                maze[mid_y][mid_x] = 0
                carve_path(nx, ny)
    
    # Start carving from the start position
    carve_path(start[0], start[1])
    
    # Ensure goal is connected (in case DFS doesn't reach it)
    if maze[goal[1]][goal[0]] != 0:
        maze[goal[1]][goal[0]] = 0
    
    return maze
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
from settings import *

class PathfindingManager:
    def __init__(self, game):
        self.game = game
        self.grid_width = int(game.map.width / TILESIZE)
        self.grid_height = int(game.map.height / TILESIZE)
        self.create_collision_grid()
    
    def create_collision_grid(self):
        """Create a grid where 1 = walkable, 0 = blocked"""
        # Start with all walkable
        self.matrix = [[1 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Mark blocked tiles from collision objects
        for block in self.game.blocks:
            # Convert pixel coordinates to grid coordinates
            start_x = int(block.rect.x / TILESIZE)
            start_y = int(block.rect.y / TILESIZE)
            end_x = int((block.rect.x + block.rect.width) / TILESIZE) + 1
            end_y = int((block.rect.y + block.rect.height) / TILESIZE) + 1
            
            # Mark all tiles in this block as unwalkable
            for y in range(start_y, min(end_y, self.grid_height)):
                for x in range(start_x, min(end_x, self.grid_width)):
                    if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                        self.matrix[y][x] = 0
    
    def find_path(self, start_pos, end_pos):
        start_x = int(start_pos[0] / TILESIZE)
        start_y = int(start_pos[1] / TILESIZE)
        end_x = int(end_pos[0] / TILESIZE)
        end_y = int(end_pos[1] / TILESIZE)
    
    # Make sure coordinates are in bounds
        start_x = max(0, min(start_x, self.grid_width - 1))
        start_y = max(0, min(start_y, self.grid_height - 1))
        end_x = max(0, min(end_x, self.grid_width - 1))
        end_y = max(0, min(end_y, self.grid_height - 1))
    
    # Create a new grid for this search
        grid = Grid(matrix=self.matrix)
    
        start = grid.node(start_x, start_y)
        end = grid.node(end_x, end_y)
    
    # Find path
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)
    
    # Convert path back to pixel coordinates
    # FIX: Use .x and .y attributes instead of subscripting
        pixel_path = [(node.x * TILESIZE + TILESIZE // 2, 
                        node.y * TILESIZE + TILESIZE // 2) for node in path]
    
        return pixel_path

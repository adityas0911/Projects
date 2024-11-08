import pygame # type: ignore
import random as rd
import numpy as np # type: ignore
import math
from enum import Enum
from transition.utils import debug_print
from .neighbor_cache import NeighborCache
from transition.mice import StationaryMouse, StochasticMouse, TwoStochasticMice

class Direction(Enum):
    LEFT = (0, -1, "LEFT")
    RIGHT = (0, 1, "RIGHT")
    UP = (-1, 0, "UP")
    DOWN = (1, 0, "DOWN")
    STAY = (0, 0, "STAY")

class GameState:
    """
    Represents the current state of the game, including the ship layout, bot and mouse positions.

    Attributes:
        BLOCKED (str): Represents a blocked cell in the ship layout.
        OPEN (str): Represents an open cell in the ship layout.
        MOUSE (str): Represents a cell occupied by a mouse.
        BOT (str): Represents a cell occupied by the bot.
        DEFAULT (str): Default cell type.
        COLOR_BLOCKED (str): Color for blocked cells.
        COLOR_OPEN (str): Color for open cells.
        COLOR_MOUSE (str): Color for mouse-occupied cells.
        COLOR_BOT (str): Color for bot-occupied cells.
        COLOR_DEFAULT (str): Default color for cells.
    """
    
    BLOCKED = 'X'
    OPEN = 'O'
    MOUSE = 'M'
    BOT = 'B'
    DEFAULT = 'D'

    COLOR_BLOCKED = "black"
    COLOR_OPEN = "white"
    COLOR_MOUSE = "red"
    COLOR_BOT = "blue"
    COLOR_DEFAULT = "gray"
    
    def __init__(self, display_dimension, ship_layout, headless=False, bot_position=None, mouse_positions=None):
        """
        Initialize the GameState.

        Args:
            display_dimension (int): The dimension of the display window.
            ship_layout (list): 2D list representing the ship's layout.
            headless (bool): If True, run without GUI. Defaults to False.
            fixed_positions (tuple): Fixed starting positions for bot and mice. Defaults to None.
        """
        self.display_dimension = display_dimension
        self.ship_layout = ship_layout
        self.D = len(ship_layout)
        self.SPLIT = display_dimension / self.D
        self.headless = headless
        self.open_cells = self.get_open_cells()
        self.bot_position = bot_position or self.place_bot()
        self.mouse_positions = mouse_positions or self.place_mice()
        self.probability_model = None
        self.neighbor_cache = NeighborCache(self.D, self.is_valid_cell)
        
        if not self.headless:
            self.screen, self.clock = self.initialize_pygame()
            self.test_surface = pygame.Surface((math.ceil(self.SPLIT), math.ceil(self.SPLIT)))
        else:
            self.screen = None
            self.clock = None
            self.test_surface = None

    def initialize_pygame(self):
        """
        Initialize Pygame for GUI representation of the game.

        Returns:
            tuple: Pygame screen and clock objects, or (None, None) if in headless mode.
        """
        if not self.headless:
            pygame.init()
            screen = pygame.display.set_mode((self.display_dimension, self.display_dimension))
            pygame.display.set_caption("Intruder Alert")
            clock = pygame.time.Clock()
            return screen, clock
        return None, None
    
    def modify_caption(self, text):
        """
        Modify the Pygame window caption.

        Args:
            text (str): New caption text.
        """
        if not self.headless:
            pygame.display.set_caption(text)

    def place_bot(self):
        return random.choice(self.open_cells)

    def place_mice(self):
        available_cells = [cell for cell in self.open_cells if cell != self.bot_position]
        return random.sample(available_cells, 2)

    def draw_ship(self):
        """
        Draw the ship layout, including probabilities if available.
        """
        if self.headless:
            return
        for x in range(self.D):
            for y in range(self.D):
                color = self.get_color(self.ship_layout[x][y])
                self.test_surface.fill(color)
                self.screen.blit(self.test_surface, (y * self.SPLIT, x * self.SPLIT))
                
                # Draw probability if available
                if self.probability_model is not None:
                    prob = self.probability_model.probability_matrix[x, y]
                    if prob > 0:
                        font = pygame.font.Font(None, int(self.SPLIT * 0.2))
                        text = font.render(f"{prob:.4f}", True, (0, 0, 0))
                        text_rect = text.get_rect(center=(y * self.SPLIT + self.SPLIT / 2, x * self.SPLIT + self.SPLIT / 2))
                        self.screen.blit(text, text_rect)

    def set_probability_model(self, model):
        """
        Set the probability model for the game state.

        Args:
            model: The probability model to set.
        """
        self.probability_model = model

    def get_probability_model(self):
        """
        Get the current probability model.

        Returns:
            The current probability model.
        """
        return self.probability_model

    def get_color(self, cell_type):
        """
        Get the color for a given cell type.

        Args:
            cell_type (str): The type of the cell.

        Returns:
            str: The color corresponding to the cell type.
        """
        return {
            self.BLOCKED: self.COLOR_BLOCKED,
            self.OPEN: self.COLOR_OPEN,
            self.MOUSE: self.COLOR_MOUSE,
            self.BOT: self.COLOR_BOT,
        }.get(cell_type, self.COLOR_DEFAULT)

    def draw_bot_and_mouse(self):
        """
        Draw the bot and mice on the game screen.
        """
        if self.headless:
            return
        self.test_surface.fill(self.COLOR_BOT)
        self.screen.blit(self.test_surface, (self.bot_position[1] * self.SPLIT, self.bot_position[0] * self.SPLIT))
        for mouse_position in self.mouse_positions:
            self.test_surface.fill(self.COLOR_MOUSE)
            self.screen.blit(self.test_surface, (mouse_position[1] * self.SPLIT, mouse_position[0] * self.SPLIT))

    def is_valid_cell(self, row, col):
        return (0 <= row < self.D and 0 <= col < self.D and
                self.get_cell_type((row, col)) != self.BLOCKED)

    def get_direction(self, old_position, new_position):
        """
        Get the direction of movement from an old position to a new position.
        
        Args:
            old_position (tuple): The old position.
            new_position (tuple): The new position.
            
        Returns:
            Direction: The direction of movement.
        """
        dx = new_position[0] - old_position[0]
        dy = new_position[1] - old_position[1]
        for direction in Direction:
            if (dx, dy) == direction.value[:2]:
                return direction
        return Direction.STAY

    def update_bot_position(self, new_position):
        """
        Update the bot's position on the game board.

        Args:
            new_position (tuple): The new position for the bot.

        Returns:
            bool: True if the bot moved, False otherwise.
        """
        direction = self.get_direction(self.bot_position, new_position)

        if self.get_cell_type(new_position) == self.BLOCKED:
            debug_print(f"Bot attempted to move {direction.value[2]} to a blocked cell at ({new_position[0]}, {new_position[1]})")
            return False  

        if new_position == self.bot_position:
            debug_print(f"{direction.value[2]}")
            return False 

        # Clear old bot position
        if not self.headless:
            self.clear_position(self.bot_position)

        # Update bot position
        old_position = self.bot_position
        self.bot_position = new_position

        # Update neighbor cache if necessary
        if self.get_cell_type(new_position) != self.get_cell_type(old_position):
            self.neighbor_cache.update_cell(new_position[0], new_position[1], True)
            self.neighbor_cache.update_cell(old_position[0], old_position[1], True)

        # Draw new bot position
        if not self.headless:
            self.draw_position(self.bot_position, self.COLOR_BOT)

        debug_print(f"{direction.value[2]} from ({old_position[0]}, {old_position[1]}) to ({self.bot_position[0]}, {self.bot_position[1]})")
        return True

    def update_mouse_positions(self, new_positions):
        """
        Update the positions of the mice on the game board.

        Args:
            new_positions (list): List of new positions for the mice.
        """
        # Ensure new_positions is a list
        if not isinstance(new_positions, list):
            new_positions = [new_positions]

        # Clear old mouse positions
        if not self.headless:
            for pos in self.mouse_positions:
                self.clear_position(pos)

        # Update mouse positions, skipping any removed mice
        old_positions = self.mouse_positions
        self.mouse_positions = [pos for pos in new_positions if pos != (-1, -1)]

        # Update neighbor cache and get movement directions
        movements = []
        for old_pos, new_pos in zip(old_positions, new_positions):
            if old_pos != new_pos:
                self.neighbor_cache.update_cell(old_pos[0], old_pos[1], True)
                self.neighbor_cache.update_cell(new_pos[0], new_pos[1], True)
                direction = self.get_direction(old_pos, new_pos)
                movements.append(f"Mouse moved {direction.value[2]} from {old_pos} to {new_pos}")
            else:
                movements.append(f"Mouse stayed at {old_pos}")

        # Draw new mouse positions
        if not self.headless:
            for pos in self.mouse_positions:
                self.draw_position(pos, self.COLOR_MOUSE)

        # Debug print with movement information
        debug_print("Mouse movements:")
        for movement in movements:
            debug_print(movement)
        debug_print(f"Updated mouse positions: {self.mouse_positions}")

    def clear_position(self, position):
        """
        Clear a position on the game board (set it to open).

        Args:
            position (tuple): The position to clear.
        """
        if not self.headless:
            self.test_surface.fill(self.COLOR_OPEN)
            self.screen.blit(self.test_surface, (position[1] * self.SPLIT, position[0] * self.SPLIT))

    def draw_position(self, position, color):
        """
        Draw a colored square at a given position on the game board.

        Args:
            position (tuple): The position to draw at.
            color (str): The color to draw with.
        """
        if not self.headless:
            self.test_surface.fill(color)
            self.screen.blit(self.test_surface, (position[1] * self.SPLIT, position[0] * self.SPLIT))

    def get_cell_type(self, position):
        """
        Get the type of cell at a given position.

        Args:
            position (tuple): The position to check.

        Returns:
            str: The type of the cell (BLOCKED, OPEN, MOUSE, BOT, or DEFAULT).
        """
        x, y = position
        if not (0 <= x < self.D and 0 <= y < self.D):
            return self.BLOCKED
        if position == self.bot_position:
            return self.BOT
        elif position in self.mouse_positions:
            return self.MOUSE
        else:
            return self.ship_layout[x][y]
        
    def get_open_cells(self):
        """
        Get all open cells in the ship layout.

        Returns:
            list: List of tuples representing open cell positions.
        """
        return [(x, y) for x in range(self.D) for y in range(self.D) if self.ship_layout[x][y] == self.OPEN]
    
    def get_neighbors(self, position):
        """
        Get the neighboring cells of a given position.

        Args:
            position (tuple): The position to get neighbors for.

        Returns:
            list: List of tuples representing neighboring cell positions.
        """
        row, col = position
        return self.neighbor_cache.get_neighbors(row, col)
    
    def is_within_bounds(self, position):
        """
        Check if a given position is within the bounds of the game board.

        Args:
            position (tuple): The position to check.

        Returns:
            bool: True if the position is within bounds, False otherwise.
        """
        x, y = position
        return 0 <= x < self.D and 0 <= y < self.D
        return [n for n in neighbors if self.get_cell_type(n) == self.OPEN]
    
    def print_game_state(self, mouse_instance):
        """
        Generate a string representation of the current game state, including the ship layout, bot position, and mouse positions.
        
        Args:
            mouse_instance: The current mouse instance (StationaryMouse, StochasticMouse, or TwoStochasticMice)
        """
        # Create a copy of the ship layout to modify
        state_grid = [row[:] for row in self.ship_layout]

        # Mark the bot position
        state_grid[self.bot_position[0]][self.bot_position[1]] = self.BOT

        # Mark the mouse positions
        if isinstance(mouse_instance, TwoStochasticMice):
            for i, mouse_pos in enumerate(mouse_instance.get_positions()):
                if mouse_pos != (-1, -1):  # Check if the mouse is not caught
                    state_grid[mouse_pos[0]][mouse_pos[1]] = f'M{i+1}'
        else:
            mouse_pos = mouse_instance.get_position()
            if mouse_pos != (-1, -1):
                state_grid[mouse_pos[0]][mouse_pos[1]] = 'M'

        # Generate the game state string
        state_string = "\nCurrent Game State:\n"
        state_string += "  " + " ".join(f"{i:2d}" for i in range(self.D)) + "\n"
        for i, row in enumerate(state_grid):
            state_string += f"{i:2d} " + " ".join(f"{cell:>2}" for cell in row) + "\n"

        # Add additional information
        state_string += f"\nBot Position: {self.bot_position}\n"

        # Adjust mouse position print based on mouse type
        if isinstance(mouse_instance, TwoStochasticMice):
            state_string += "Mouse Positions:\n"
            for i, pos in enumerate(mouse_instance.get_positions()):
                if pos != (-1, -1):
                    state_string += f"  Mouse {i+1}: {pos}\n"
                else:
                    state_string += f"  Mouse {i+1}: Caught\n"
        else:
            mouse_pos = mouse_instance.get_position()
            if mouse_pos != (-1, -1):
                state_string += f"Mouse Position: {mouse_pos}\n"
            else:
                state_string += "Mouse: Caught\n"

        # Print the generated string
        debug_print(state_string)
        
    def print_ship_state(self, step_counter):
        """
        Print the ship state as a float matrix where open cells are 0 and blocked cells are 1.
        Does not include bot or mouse positions.
        """
        state_matrix = np.zeros((self.D, self.D), dtype=int)
        for i in range(self.D):
            for j in range(self.D):
                if self.ship_layout[i][j] == self.BLOCKED:
                    state_matrix[i, j] = 1
        
        # Convert matrix to string with commas
        matrix_string = '[[' + '],\n ['.join([', '.join(map(str, row)) for row in state_matrix]) + ']]'
        grid_print(f"{step_counter}:\n{matrix_string}")

    def print_bot_state(self, step_counter):
        """
        Print the bot state as a float matrix where all cells are 0 except the bot position which is 1.
        """
        bot_matrix = np.zeros((self.D, self.D), dtype=int)
        bot_matrix[self.bot_position[0], self.bot_position[1]] = 1
        
        # Convert matrix to string with commas
        matrix_string = '[[' + '],\n ['.join([', '.join(map(str, row)) for row in bot_matrix]) + ']]'
        bot_position_print(f"{step_counter}:\n{matrix_string}")
            
    def print_bot_action(self, step_counter):
        """
        Print the bot's action as an array using the action_print logger.
        The action is determined by comparing the current position to the previous position.
        """
        action_array = np.zeros(5, dtype=int)
        
        if not hasattr(self, 'previous_bot_position'):
            self.previous_bot_position = self.bot_position
            action_array[4] = 1  # Assume initial action is SENSE
        else:
            direction = self.get_direction(self.previous_bot_position, self.bot_position)
            
            action_index = {
                Direction.LEFT: 0,
                Direction.RIGHT: 1,
                Direction.UP: 2,
                Direction.DOWN: 3,
                Direction.STAY: 4  # Treat STAY as SENSE
            }
            
            action_array[action_index[direction]] = 1
            
            # Update previous position for next call
            self.previous_bot_position = self.bot_position

        # Convert the numpy array to a string with commas
        action_string = '[' + ', '.join(map(str, action_array)) + ']'
        
        action_print(f"{step_counter}:\n{action_string}")
        
    def get_ship_state_matrix(self):
        return [[1 if cell == self.BLOCKED else 0 for cell in row] for row in self.ship_layout]

    def get_bot_state_matrix(self):
        matrix = [[0 for _ in range(self.D)] for _ in range(self.D)]
        matrix[self.bot_position[0]][self.bot_position[1]] = 1
        return matrix

    def get_bot_action(self):
        if not hasattr(self, 'previous_bot_position'):
            self.previous_bot_position = self.bot_position
            return 0  # Initial action is STAY/SENSE

        direction = self.get_direction(self.previous_bot_position, self.bot_position)
        
        action_index = {
            Direction.STAY: 0,  # STAY/SENSE
            Direction.UP: 1,
            Direction.RIGHT: 2,
            Direction.DOWN: 3,
            Direction.LEFT: 4
        }

        self.previous_bot_position = self.bot_position
        return action_index[direction]
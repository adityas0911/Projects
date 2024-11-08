import pygame
import random as rd
import math
from transition.utils import debug_print

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
    
    def __init__(self, display_dimension, ship_layout, headless=False, fixed_positions=None):
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
        self.bot_position, mouse_positions = fixed_positions or self.place_bot_and_mouse()
        self.mouse_positions = mouse_positions if isinstance(mouse_positions, list) else [mouse_positions]
        self.probability_model = None
        
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

    def place_bot_and_mouse(self):
        """
        Randomly place the bot and mice on open cells.

        Returns:
            tuple: Bot position and list of mouse positions.
        """
        open_cells = self.get_open_cells()
        bot_position = rd.choice(open_cells)
        open_cells.remove(bot_position)
        mouse_positions = rd.sample(open_cells, 2)
        return bot_position, mouse_positions

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

    def update_bot_position(self, new_position):
        """
        Update the bot's position on the game board.

        Args:
            new_position (tuple): The new position for the bot.

        Returns:
            bool: True if the bot moved, False otherwise.
        """
        if self.get_cell_type(new_position) == self.BLOCKED:
            debug_print(f"Bot attempted to move to a blocked cell at {new_position}")
            return False  

        if new_position == self.bot_position:
            debug_print(f"Bot stayed in: {self.bot_position}")
            return False 

        # Clear old bot position
        if not self.headless:
            self.clear_position(self.bot_position)
    
        # Update bot position
        old_position = self.bot_position
        self.bot_position = new_position
    
        # Draw new bot position
        if not self.headless:
            self.draw_position(self.bot_position, self.COLOR_BOT)

        debug_print(f"Bot moved from {old_position} to {self.bot_position}")
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
        self.mouse_positions = [pos for pos in new_positions if pos != (-1, -1)]

        # Draw new mouse positions
        if not self.headless:
            for pos in self.mouse_positions:
                self.draw_position(pos, self.COLOR_MOUSE)

        debug_print(f"Mouse positions updated to {self.mouse_positions}")

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
        x, y = position
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    
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
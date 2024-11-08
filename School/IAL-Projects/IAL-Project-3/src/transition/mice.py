from abc import ABC, abstractmethod
import random

class BaseMouse(ABC):
    """
    Abstract base class for all mouse types in the game.

    This class defines the basic structure and interface for mouse objects.
    """
    
    def __init__(self, initial_position, game_state):
        """
        Initialize a BaseMouse object.

        Args:
            initial_position (tuple): The starting position of the mouse.
            game_state (GameState): The current state of the game.
        """
        self.position = initial_position
        self.game_state = game_state
        self.type = None

    @abstractmethod
    def move(self):
        """
        Abstract method to define the mouse's movement.

        This method should be implemented by all subclasses.
        """
        pass

    def get_position(self):
        """
        Get the current position of the mouse.

        Returns:
            tuple: The current (x, y) position of the mouse.
        """
        return self.position

    def update_position(self, new_position):
        """
        Update the mouse's position if the new position is valid.

        Args:
            new_position (tuple): The proposed new position for the mouse.

        Returns:
            bool: True if the position was updated, False otherwise.
        """
        if self.game_state.is_within_bounds(new_position) and self.game_state.get_cell_type(new_position) != self.game_state.BLOCKED and self.game_state.get_cell_type(new_position) != self.game_state.BOT:
            self.position = new_position
            return True
        return False

class StationaryMouse(BaseMouse):
    """
    Represents a stationary mouse that does not move.
    """

    def __init__(self, initial_position, game_state):
        """
        Initialize a StationaryMouse object.

        Args:
            initial_position (tuple): The starting position of the mouse.
            game_state (GameState): The current state of the game.
        """
        super().__init__(initial_position, game_state)
        self.type = "Stationary Mouse"
    
    def move(self):
        """
        The stationary mouse does not move, so this method does nothing.
        """
        pass

class StochasticMouse(BaseMouse):
    """
    Represents a mouse that moves randomly to adjacent cells.
    """

    def __init__(self, initial_position, game_state):
        """
        Initialize a StochasticMouse object.

        Args:
            initial_position (tuple): The starting position of the mouse.
            game_state (GameState): The current state of the game.
        """
        super().__init__(initial_position, game_state)
        self.type = "Stochastic Mouse"
    
    def move(self):
        """
        Move the mouse to a random adjacent cell or stay in place.

        The mouse attempts to move in a random direction (including staying still).
        If the chosen direction is blocked or out of bounds, it tries other directions.
        """
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
        random.shuffle(possible_moves)  # Shuffle the moves to avoid bias
        
        for dx, dy in possible_moves:
            new_x, new_y = self.position[0] + dx, self.position[1] + dy
            if self.update_position((new_x, new_y)):
                break
            
class TwoStochasticMice(BaseMouse):
    """
    Represents two stochastic mice that move independently.
    """
    
    def __init__(self, initial_positions, game_state):
        """
        Initialize a TwoStochasticMice object.

        Args:
            initial_positions (list): A list of two tuples representing the starting positions of the mice.
            game_state (GameState): The current state of the game.
        """
        super().__init__(initial_positions[0], game_state)
        self.positions = initial_positions
        self.type = "TwoStochastic Mice"
        self.caught = [False, False]  # Track the caught status of each mouse

    def move(self):
        """
        Move both mice independently to random adjacent cells or stay in place.

        Each mouse attempts to move in a random direction (including staying still).
        If the chosen direction is blocked or out of bounds, it tries other directions.
        """
        new_positions = []
        for i, pos in enumerate(self.positions):
            if self.caught[i]:  # Skip movement if the mouse is caught
                new_positions.append((-1, -1))  # Keep the invalid position
                continue
            
            possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
            random.shuffle(possible_moves)
            
            for dx, dy in possible_moves:
                new_x, new_y = pos[0] + dx, pos[1] + dy
                if self.update_position(i, (new_x, new_y)):
                    new_positions.append((new_x, new_y))
                    break
            else:
                new_positions.append(pos)
        
        self.positions = new_positions

    def get_positions(self):
        """
        Get the current positions of both mice.

        Returns:
            list: A list of two tuples representing the current positions of the mice.
        """
        return self.positions

    def update_position(self, mouse_index, new_position):
        """
        Update the position of a specific mouse if the new position is valid.

        Args:
            mouse_index (int): The index of the mouse (0 or 1).
            new_position (tuple): The proposed new position for the mouse.

        Returns:
            bool: True if the position was updated, False otherwise.
        """
        if (self.game_state.is_within_bounds(new_position) and 
            self.game_state.get_cell_type(new_position) != self.game_state.BLOCKED and 
            self.game_state.get_cell_type(new_position) != self.game_state.BOT and
            new_position != self.positions[1 - mouse_index]):
            return True
        return False

    def update_positions(self, new_positions):
        """
        Update the positions of both mice if the new positions are valid.

        Args:
            new_positions (list): A list of two tuples representing the proposed new positions for the mice.
        """
        updated_positions = []
        for i, new_pos in enumerate(new_positions):
            if self.update_position(i, new_pos):
                updated_positions.append(new_pos)
            else:
                updated_positions.append(self.positions[i])
        self.positions = updated_positions

    def catch_mouse(self, bot_position):
        """
        Mark a mouse as caught if it's in the same position as the bot.

        Args:
            bot_position (tuple): The current position of the bot.
        """
        for i, pos in enumerate(self.positions):
            if pos == bot_position:
                self.caught[i] = True
                self.positions[i] = (-1, -1)  # Set to an invalid position to indicate removal

    def is_caught(self, mouse_index):
        """
        Check if a specific mouse has been caught.

        Args:
            mouse_index (int): The index of the mouse to check (0 or 1).

        Returns:
            bool: True if the mouse has been caught, False otherwise.
        """
        return self.caught[mouse_index]
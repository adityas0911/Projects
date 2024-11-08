from abc import ABC, abstractmethod
import numpy as np
import random as rd
from transition.bayesian_network import ProbabilityModel, manhattan_distance, shortest_path, possible_neighbors
from transition.utils import debug_print

class Bot(ABC):
    """
    Abstract base class for all bot types in the game.

    This class defines the basic structure and interface for bot objects.
    """
    
    def __init__(self, game_state, alpha):
        """
        Initialize a Bot object.

        Args:
            game_state (GameState): The current state of the game.
            alpha (float): The sensitivity parameter for the bot's sensor.
        """
        self.bot_num = 0
        self.game_state = game_state
        self.alpha = alpha
        self.position = game_state.bot_position
        self.highest_prob_cell = None
        self.shortest_path = []
        self.prob_model = ProbabilityModel(game_state)
        self.game_state.set_probability_model(self.prob_model)
        self.last_sense_result = None

    @abstractmethod
    def move(self):
        """
        Abstract method to define the bot's movement strategy.

        This method should be implemented by all subclasses.

        Returns:
            tuple: The new position of the bot.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def sense(self):
        """
        Perform a sensing action to detect nearby mice.

        Returns:
            bool: True if a beep is heard, False otherwise.
        """
        mouse_positions = self.game_state.mouse_positions if isinstance(self.game_state.mouse_positions, list) else [self.game_state.mouse_position]
        distances = [manhattan_distance(self.game_state, self.position, mouse_pos) for mouse_pos in mouse_positions]
        min_distance = min(distances)
        beep_probability = 0.001 if min_distance is None else np.exp(-self.alpha * (min_distance - 1))
        beep = rd.random() < beep_probability
        self.last_sense_result = beep
        debug_print(f"Beep probability: {beep_probability}, Beep: {beep}")
        return beep

    def get_highest_probability_cells(self):
        """
        Get all cells with the highest probability of containing a mouse.

        Returns:
            list: A list of tuples representing the cells with the highest probability.
        """
        prob_matrix = self.prob_model.get_probability_grid()
        prob_matrix[self.position] = 0  # Exclude current position
        max_prob = np.max(prob_matrix)
        highest_prob_cells = list(zip(*np.where(prob_matrix == max_prob)))
        return [(int(x), int(y)) for x, y in highest_prob_cells]

    def choose_closest_cell(self, cells):
        """
        Choose the closest cell from a list of cells.

        Args:
            cells (list): A list of cell positions to choose from.

        Returns:
            tuple: The chosen cell position.
        """
        distances = [manhattan_distance(self.game_state, self.position, cell) for cell in cells]
        min_distance = min(distances)
        closest_cells = [cell for cell, distance in zip(cells, distances) if distance == min_distance]
        chosen_cell = rd.choice(closest_cells)
        debug_print(f"Chosen cell from {len(closest_cells)} equally close cells: {chosen_cell}")
        return chosen_cell

    def get_highest_probability_cell(self):
        """
        Get the cell with the highest probability of containing a mouse.

        Returns:
            tuple: The position of the cell with the highest probability.
        """
        highest_prob_cells = self.get_highest_probability_cells()
        highest_prob = self.prob_model.get_probability_grid()[highest_prob_cells[0]]
        debug_print(f"Highest probability cells: {highest_prob_cells}")
        debug_print(f"Highest probability: {highest_prob}")
        return self.choose_closest_cell(highest_prob_cells) if highest_prob_cells else self.position

    def update_probabilities(self, beep):
        """
        Update the probability model based on the sensing result.

        Args:
            beep (bool): Whether a beep was heard or not.
            num_mice (int): The number of mice in the game.
        """
        if beep:
            self.prob_model.update_on_beep(self.position, self.alpha)
        else:
            self.prob_model.update_on_no_beep(self.position, self.alpha)
        self.prob_model.set_cell_probability(self.position, 0)
        self.prob_model.normalize()

    def log_probabilities(self):
        """
        Log the current probability matrix for debugging purposes.
        """
        debug_print("Updated probabilities")
        debug_print(np.array2string(self.prob_model.get_probability_grid(), precision=4, suppress_small=True))
        debug_print("Sum of probabilities: ", self.prob_model.sum_probabilities())

    def move_to_new_position(self, new_position):
        """
        Move the bot to a new position if it's not blocked.

        Args:
            new_position (tuple): The new position to move to.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if self.game_state.get_cell_type(new_position) != self.game_state.BLOCKED:
            self.prob_model.update_on_bot_move(new_position)
            self.position = new_position
            return True
        return False

class Bot1(Bot):
    """
    Bot1 implementation: Move to the location with highest probability, then sense.
    """
    
    def __init__(self, game_state, alpha):
        """
        Initialize Bot1.

        Args:
            game_state (GameState): The current state of the game.
            alpha (float): The sensitivity parameter for the bot's sensor.
        """
        super().__init__(game_state, alpha)
        self.bot_num = 1

    def move(self):
        """
        Bot moves to the location with the highest probability of containing a mouse and then senses.
        
        Args:
            num_mice (int): The number of mice in the game.

        Returns:
            tuple: The new position of the bot.
        """
        # Check if the bot has reached the highest probability cell or if it's the first step
        if self.highest_prob_cell is None or self.position == self.highest_prob_cell:
            debug_print("Updating new highest probability cell and path")
            beep = self.sense()
            debug_print(f"Beep: {beep}")
            self.update_probabilities(beep)
            self.log_probabilities()

            self.highest_prob_cell = self.get_highest_probability_cell()
            self.shortest_path = shortest_path(self.game_state, self.position, self.highest_prob_cell)
            return self.position

        # Check if the bot has sensed, and if so, move to highest probability cell
        if self.shortest_path:
            new_position = self.shortest_path.pop(0)
            if self.move_to_new_position(new_position):
                return new_position
        else:
            # If the bot is stuck and has no path, move to the highest probability neighbor
            neighbors = possible_neighbors(self.game_state, self.position)
            new_position = max(neighbors, key=lambda pos: self.prob_model.get_probability_grid()[pos[0]][pos[1]])

        return self.position

class Bot2(Bot):
    """
    Bot2 implementation: Move toward the location with highest probability, alternate moving and sensing.
    """
    
    def __init__(self, game_state, alpha):
        """
        Initialize Bot2.

        Args:
            game_state (GameState): The current state of the game.
            alpha (float): The sensitivity parameter for the bot's sensor.
        """
        super().__init__(game_state, alpha)
        self.should_sense = True
        self.bot_num = 2

    def move(self):
        """
        Implement the movement strategy for Bot2, initially senses and then moves toward the highest probability cell. Alternates between moving and sensing on each step.

        Args:
            num_mice (int): The number of mice in the game.

        Returns:
            tuple: The new position of the bot.
        """
        # Bot should sense first
        if self.should_sense:
            beep = self.sense()
            debug_print(f"Beep: {beep}")
            self.update_probabilities(beep)
            self.log_probabilities()

            self.highest_prob_cell = self.get_highest_probability_cell()
            self.shortest_path = shortest_path(self.game_state, self.position, self.highest_prob_cell)
            self.should_sense = False
            return self.position

        # Check if the bot has sensed, and if so, move toward highest probability cell
        if self.shortest_path:
            new_position = self.shortest_path.pop(0)
            if self.move_to_new_position(new_position):
                self.should_sense = True
                return new_position
        else:
            # If the bot is stuck and has no path, move to the highest probability neighbor
            neighbors = possible_neighbors(self.game_state, self.position)
            new_position = max(neighbors, key=lambda pos: self.prob_model.get_probability_grid()[pos[0]][pos[1]])

        return self.position

class Bot3(Bot):
    """
    Bot3 implementation: Uses a dynamic uncertainty threshold and maximum steps without sensing to decide when to sense. Initializes uncertainty threshold to be lower to reflect the initial uncertainty of the grid and adjusts dynamically based on the maximum probability and an uncertainty adjustment factor. The bot also dynamically adjusts the uncertainty threshold based on the maximum probability to ensure that it senses more frequently when the probability of finding a mouse is higher.
    
    Keeps track of steps since last sensing and compares it to the maximum steps without sensing, which is updated on sense to be half the length of the current path to the highest probability cell. This allows for more frequent sensing when the bot is far from the highest probability cell and less frequent sensing when the bot is close to the highest probability cell. Allowing the bot to take more steps toward the highest probability cell before sensing again.
    
    In this way, the bot can balance sensing and moving dynamically reflecting the current state of the grid.
    """
    
    def __init__(self, game_state, alpha):
        """
        Initialize Bot3.

        Args:
            game_state (GameState): The current state of the game.
            alpha (float): The sensitivity parameter for the bot's sensor.
        """
        super().__init__(game_state, alpha)
        self.bot_num = 3
        self.steps_since_last_sense = 0
        self.max_steps_without_sensing = 5
        self.base_uncertainty_threshold = 0.05
        self.uncertainty_threshold = 0.05
        self.uncertainty_adjustment_factor = 0.5        
        self.highest_prob_cell = None
        self.should_sense_flag = True

    def move(self):
        """
        Implement the movement strategy for Bot3, checks if sense flag is set, if so, senses and updates probabilities.  Once the bot senses, it adjusts the maximum steps without sensing is updated to be half the length of the current path to the highest probability cell. 

        Args:
            num_mice (int): The number of mice in the game.

        Returns:
            tuple: The new position of the bot.
        """
        debug_print(f"Current position: {self.position}")

        # Check if the bot should sense and reset variables
        if self.should_sense_flag:
            beep = self.sense()
            debug_print(f"Beep: {beep}")
            self.update_probabilities(beep)
            self.log_probabilities()
            self.steps_since_last_sense = 0
            self.shortest_path = []
            self.highest_prob_cell = None
            self.should_sense_flag = False
        
        # If the bot doesn't have a path to the highest probability cell, get a new one
        if not self.shortest_path:
            self.highest_prob_cell = self.get_highest_probability_cell()
            debug_print(f"New target: {self.highest_prob_cell}")
            self.shortest_path = shortest_path(self.game_state, self.position, self.highest_prob_cell)
            debug_print(f"New path: {self.shortest_path}")
            self.max_steps_without_sensing = len(self.shortest_path) / 2

        # Get cell to move to
        new_position = self.position
        if self.shortest_path:
            new_position = self.shortest_path.pop(0)
        else:
            # If the bot is stuck and has no path, move to the highest probability neighbor
            neighbors = possible_neighbors(self.game_state, self.position)
            new_position = max(neighbors, key=lambda pos: self.prob_model.get_probability_grid()[pos[0]][pos[1]])

        # Move to the new position and update steps since last sense
        if self.move_to_new_position(new_position):
            self.steps_since_last_sense += 1
            debug_print(f"Moving to: {self.position}")
        else:
            debug_print(f"Attempted move to blocked cell {new_position}, staying in place")

        # Determine if the bot should sense on next step
        if self.should_sense():
            self.should_sense_flag = True

        debug_print(f"Steps since last sense: {self.steps_since_last_sense}")
        return self.position

    def should_sense(self):
        """
        Determine if the bot should perform a sensing action.

        Returns:
            bool: True if the bot should sense, False otherwise.
        """
        max_prob = np.max(self.prob_model.get_probability_grid())
        
        # Dynamically adjust the uncertainty threshold
        self.uncertainty_threshold = self.base_uncertainty_threshold + (max_prob * self.uncertainty_adjustment_factor)
        
        debug_print(f"Max probability: {max_prob}, Adjusted uncertainty threshold: {self.uncertainty_threshold}")
        debug_print(f"Steps since last sense: {self.steps_since_last_sense}")
        
        return max_prob < self.uncertainty_threshold or self.steps_since_last_sense >= self.max_steps_without_sensing
    
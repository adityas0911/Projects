import math
import heapq
import numpy as np
from collections import defaultdict
from transition.utils import debug_print

class ProbabilityModel:
    """
    Represents a probability model for the mouse's location in the ship.

    This class manages and updates probabilities for each cell in the ship layout.
    """
    def __init__(self, game_state):
        """
        Initialize the ProbabilityModel.

        Args:
            game_state (GameState): The current state of the game.
        """
        self.game_state = game_state
        self.grid_size = game_state.D
        self.probability_matrix = self.initialize_probabilities()

    def initialize_probabilities(self):
        """
        Initialize the probability matrix with uniform probabilities for open cells.

        Returns:
            numpy.ndarray: The initialized probability matrix.
        """
        prob_matrix = np.zeros((self.grid_size, self.grid_size))
        open_cells = self.game_state.get_open_cells()
        uniform_prob = 1.0 / len(open_cells)
        for x, y in open_cells:
            prob_matrix[x, y] = uniform_prob
        return prob_matrix

    def normalize(self, matrix=None):
        """
        Normalize the probability matrix so that all probabilities sum to 1, calls check_probability_sum to check if the sum is close to 1.

        Args:
            matrix (numpy.ndarray, optional): The matrix to normalize. If None, normalizes the instance's probability matrix.

        Returns:
            numpy.ndarray: The normalized probability matrix.
        """
        if matrix is None:
            matrix = self.probability_matrix
        total = np.sum(matrix)
        normalized = matrix / (total + 1e-10) if total > 0 else self.initialize_probabilities()
        self.check_probability_sum(normalized)
        return normalized

    def beep_probability(self, bot_position, alpha, row, col):
        """
        Calculate the probability of hearing a beep given the bot and mouse positions.

        Args:
            bot_position (tuple): The current position of the bot.
            alpha (float): The sensitivity parameter for the bot's sensor.
            row (int): The row of the cell to calculate the probability for.
            col (int): The column of the cell to calculate the probability for.

        Returns:
            float: The probability of hearing a beep.
        """
        probability_no_beep = 1
        num_mice = len(self.game_state.mouse_positions)
        while num_mice > 0:
            num_mice -= 1
            d = manhattan_distance(self.game_state, (row, col), bot_position)
            if d is not None:
                probability_no_beep *= (1 - np.exp(-alpha * (d - 1)))
        probability_beep = 1 - probability_no_beep
        return probability_beep

    def update_on_beep(self, bot_position, alpha):
        """
        Update the probability matrix when a beep is heard.

        Args:
            bot_position (tuple): The current position of the bot.
            alpha (float): The sensitivity parameter for the bot's sensor.
        """
        debug_print(f"Before beep update - Sum of probabilities: {self.sum_probabilities()}")
        updated_matrix = np.zeros((self.grid_size, self.grid_size))
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                beep_probability = self.beep_probability(bot_position, alpha, row, col)
                updated_matrix[row, col] = beep_probability * self.probability_matrix[row, col]
        self.probability_matrix = self.normalize(updated_matrix)
        debug_print(f"After beep update - Sum of probabilities: {self.sum_probabilities()}")

    def update_on_no_beep(self, bot_position, alpha):
        """
        Update the probability matrix when no beep is heard.

        Args:
            bot_position (tuple): The current position of the bot.
            alpha (float): The sensitivity parameter for the bot's sensor.
        """
        debug_print(f"Before no-beep update - Sum of probabilities: {self.sum_probabilities()}")
        updated_matrix = np.zeros((self.grid_size, self.grid_size))
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                no_beep_probability = 1 - self.beep_probability(bot_position, alpha, row, col)
                updated_matrix[row, col] = no_beep_probability * self.probability_matrix[row, col]
        self.probability_matrix = self.normalize(updated_matrix)
        debug_print(f"After no-beep update - Sum of probabilities: {self.sum_probabilities()}")

    def update_on_bot_move(self, new_position):
        """
        Update the probability matrix when the bot moves, zeroing out the probability of the new position.

        Args:
            new_position (tuple): The new position of the bot.
        """
        debug_print(f"Before bot move update - Sum of probabilities: {self.sum_probabilities()}")
        self.probability_matrix[new_position] = 0
        self.probability_matrix = self.normalize()
        debug_print(f"After bot move update - Sum of probabilities: {self.sum_probabilities()}")

    def update_on_mouse_move(self):
        """
        Update the probability matrix to account for possible mouse/mice movement.
        """
        debug_print(f"Before mouse move update - Sum of probabilities: {self.sum_probabilities()}")
        updated_matrix = np.zeros_like(self.probability_matrix)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.game_state.get_cell_type((row, col)) != self.game_state.BLOCKED:
                    neighbors = self.get_valid_neighbors(row, col)
                    num_neighbors = len(neighbors) + 1
                    if num_neighbors > 0:
                        prob_stay = 1 - (1 - 1/num_neighbors)**2
                        updated_matrix[row, col] += prob_stay * self.probability_matrix[row, col]
                        prob_move = 1/num_neighbors
                        for nr, nc in neighbors:
                            updated_matrix[nr, nc] += prob_move * self.probability_matrix[row, col]
                    else:
                        updated_matrix[row, col] += self.probability_matrix[row, col]
        self.probability_matrix = self.normalize(updated_matrix)
        debug_print(f"After mouse move update - Sum of probabilities: {self.sum_probabilities()}")

    def get_valid_neighbors(self, row, col):
        """
        Get the valid neighboring cells for a given position.

        Args:
            row (int): The row of the cell.
            col (int): The column of the cell.

        Returns:
            list: A list of tuples representing valid neighboring cell positions.
        """
        return [(row + dr, col + dc) for dr in [-1, 0, 1] for dc in [-1, 0, 1]
                if (dr != 0 or dc != 0) and 0 <= row + dr < self.grid_size and 0 <= col + dc < self.grid_size
                and self.game_state.get_cell_type((row + dr, col + dc)) != self.game_state.BLOCKED]

    def get_highest_probability_cell(self):
        """
        Get the cell with the highest probability of containing the mouse.

        Returns:
            tuple: The (row, col) of the cell with the highest probability.
        """
        return tuple(map(int, np.unravel_index(np.argmax(self.probability_matrix), self.probability_matrix.shape)))

    def print_highest_prob_cell(self):
        """
        Print the cell with the highest probability and its probability value.
        """
        highest_prob_cell = self.get_highest_probability_cell()
        debug_print(f"Highest probability cell: {highest_prob_cell}, Value: {self.probability_matrix[highest_prob_cell]}")

    def get_probability_grid(self):
        """
        Get a copy of the current probability matrix.

        Returns:
            numpy.ndarray: A copy of the current probability matrix.
        """
        return np.copy(self.probability_matrix)

    def set_cell_probability(self, position, value):
        """
        Set the probability of a specific cell.

        Args:
            position (tuple): The (row, col) of the cell.
            value (float): The probability value to set.
        """
        self.probability_matrix[position] = value

    def sum_probabilities(self):
        """
        Calculate the sum of all probabilities in the matrix.

        Returns:
            float: The sum of all probabilities.
        """
        return np.sum(self.probability_matrix)
    
    def check_probability_sum(self, matrix=None):
        """
        Check if the sum of probabilities is close to 1.0 and log a warning if not.

        Args:
            matrix (numpy.ndarray, optional): The matrix to check. If None, checks the instance's probability matrix.
        """
        if matrix is None:
            matrix = self.probability_matrix
        total = np.sum(matrix)
        if abs(total - 1.0) > 0.001:
            debug_print(f"Warning: Sum of probabilities ({total}) deviates significantly from 1.0")

    def __str__(self):
        """
        Return a string representation of the probability grid.

        Returns:
            str: A string representation of the probability grid.
        """
        return str(self.get_probability_grid())

def possible_neighbors(game_state, position):
    """
    Get the possible neighboring cells for a given position.

    Args:
        game_state (GameState): The current state of the game.
        position (tuple): The (row, col) of the cell to get neighbors for.

    Returns:
        list: A list of tuples representing valid neighboring cell positions.
    """
    row, column = position
    return [(row + dx, column + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if 0 <= row + dx < game_state.D and 0 <= column + dy < game_state.D
            and game_state.get_cell_type((row + dx, column + dy)) in {game_state.OPEN, game_state.MOUSE, game_state.BOT}]

def shortest_path(game_state, start_position, end_position):
    """
    Find the shortest path between two positions using A* algorithm.

    Args:
        game_state (GameState): The current state of the game.
        start_position (tuple): The starting position.
        end_position (tuple): The target position.

    Returns:
        list: A list of positions representing the shortest path.
    """
    fringe = [(0, start_position)]
    parent = {}
    distance = defaultdict(lambda: float('inf'))
    distance[start_position] = 0
    heapq.heapify(fringe)

    while fringe:
        _, current_position = heapq.heappop(fringe)
        if current_position == end_position:
            path = []
            while current_position in parent:
                path.append(current_position)
                current_position = parent[current_position]
            return path[::-1]

        for neighbor in possible_neighbors(game_state, current_position):
            distance_to_neighbor = distance[current_position] + 1
            if distance[neighbor] > distance_to_neighbor:
                distance[neighbor] = distance_to_neighbor
                heapq.heappush(fringe, (distance_to_neighbor, neighbor))
                parent[neighbor] = current_position

    return []

def manhattan_distance(game_state, start, end):
    """
    Calculate the Manhattan distance between two positions, accounting for walls.

    Args:
        game_state (GameState): The current state of the game.
        start (tuple): The starting position.
        end (tuple): The ending position.

    Returns:
        int: The Manhattan distance between the two positions, or D*D if no path exists.
    """
    if game_state.get_cell_type(start) == game_state.BLOCKED or game_state.get_cell_type(end) == game_state.BLOCKED:
        return game_state.D * game_state.D
    path = shortest_path(game_state, start, end)
    return len(path) if path else game_state.D * game_state.D
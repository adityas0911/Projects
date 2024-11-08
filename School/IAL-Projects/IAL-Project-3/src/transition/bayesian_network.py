import math
import heapq
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'c_extensions')))

from functools import lru_cache
from collections import defaultdict
from transition.utils import debug_print
from shortest_path import shortest_path as c_shortest_path

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
        self.distance_cache = {}
        self.neighbor_cache = {}

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
            d = self.manhattan_distance((row, col), bot_position)
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
        updated_matrix = np.zeros((self.grid_size, self.grid_size))
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.game_state.get_cell_type((row, col)) != self.game_state.BLOCKED:
                    beep_probability = self.beep_probability(bot_position, alpha, row, col)
                    updated_matrix[row, col] = beep_probability * self.probability_matrix[row, col]
        self.probability_matrix = self.normalize(updated_matrix)
        
    def update_on_no_beep(self, bot_position, alpha):
        """
        Update the probability matrix when no beep is heard.

        Args:
            bot_position (tuple): The current position of the bot.
            alpha (float): The sensitivity parameter for the bot's sensor.
        """
        updated_matrix = np.zeros((self.grid_size, self.grid_size))
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.game_state.get_cell_type((row, col)) != self.game_state.BLOCKED:
                    no_beep_probability = 1 - self.beep_probability(bot_position, alpha, row, col)
                    updated_matrix[row, col] = no_beep_probability * self.probability_matrix[row, col]
        self.probability_matrix = self.normalize(updated_matrix)
        
    def update_on_bot_move(self, new_position):
        """
        Update the probability matrix when the bot moves, zeroing out the probability of the new position.

        Args:
            new_position (tuple): The new position of the bot.
        """
        self.probability_matrix[new_position] = 0
        self.probability_matrix = self.normalize()
        
    def update_on_mouse_move(self):
        """
        Update the probability matrix to account for possible mouse/mice movement.
        """
        updated_matrix = np.zeros_like(self.probability_matrix)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.game_state.get_cell_type((row, col)) != self.game_state.BLOCKED:
                    neighbors = self.game_state.neighbor_cache.get_neighbors(row, col)
                    prob = self.probability_matrix[row, col] / (len(neighbors) + 1)
                    updated_matrix[row, col] += prob
                    for neighbor_row, neighbor_col in neighbors:
                        updated_matrix[neighbor_row, neighbor_col] += prob
        
        self.probability_matrix = updated_matrix
        self.normalize()

    def get_cached_neighbors(self, row, col):
        key = (row, col)
        if key not in self.neighbor_cache:
            self.neighbor_cache[key] = self.get_valid_neighbors(row, col)
        return self.neighbor_cache[key]

    def get_valid_neighbors(self, row, col):
        return self.game_state.get_neighbors((row, col))

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

    @lru_cache(maxsize=10000)
    def cached_manhattan_distance(self, start, end):
        if self.game_state.get_cell_type(start) == self.game_state.BLOCKED or self.game_state.get_cell_type(end) == self.game_state.BLOCKED:
            return self.game_state.D * self.game_state.D
        path = shortest_path(self.game_state, start, end)
        return len(path) if path else self.game_state.D * self.game_state.D

    def manhattan_distance(self, start, end):
        cache_key = (start, end)
        if cache_key in self.distance_cache:
            return self.distance_cache[cache_key]
        distance = self.cached_manhattan_distance(start, end)
        self.distance_cache[cache_key] = distance
        return distance

def shortest_path(game_state, start_position, end_position):
    grid = [1 if game_state.get_cell_type((i, j)) == game_state.BLOCKED else 0 
            for i in range(game_state.D) 
            for j in range(game_state.D)]

    result = c_shortest_path(grid, game_state.D, game_state.D, 
                             start_position[0], start_position[1], end_position[0], end_position[1])
    
    if result is None:
        return []
    
    path, distance = result
    if distance == -1:
        return []
    
    return path
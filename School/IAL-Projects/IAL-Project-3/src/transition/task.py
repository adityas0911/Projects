import pygame # type: ignore
import random as rd
import numpy as np # type: ignore
import csv
import os
from datetime import datetime
import ast
from transition.bayesian_network import ProbabilityModel
from transition.utils import debug_print, warning_print
from transition.mice import StationaryMouse, StochasticMouse, TwoStochasticMice

class Task:
    """
    Represents a single game task, managing the interaction between the bot and the mice.

    This class handles the game loop, including bot and mouse movements, and determines the outcome of the game.
    """

    def __init__(self, game_state, bot_instance, mouse_instance, alpha, delay=500, headless=False):
        """
        Initialize a Task object.

        Args:
            game_state (GameState): The current state of the game.
            bot_instance (Bot): An instance of the bot.
            mouse_instance (BaseMouse): An instance of the mouse/mice.
            alpha (float): The sensitivity parameter for the bot's sensor.
            delay (int, optional): The delay between game steps in milliseconds. Defaults to 500.
            headless (bool, optional): Whether to run the game without GUI. Defaults to False.
        """
        self.game_state = game_state
        self.bot = bot_instance 
        self.alpha = alpha
        self.step_counter = 0
        self.delay = delay
        self.headless = headless
        self.mouse = mouse_instance
        self.bot.neighbor_cache = game_state.neighbor_cache
        self.states = []

    def run(self, exit_event):
        """
        Run the game task.

        This method contains the main game loop, managing bot and mouse movements,
        checking for game end conditions, and updating the game state.

        Args:
            exit_event (threading.Event): An event to signal when the game should exit.

        Returns:
            tuple: A tuple containing the game outcome (string) and the number of steps taken.
        """
        running = True
        debug_print("Starting game loop")
        self.game_state.print_game_state(self.mouse)
        
        if not self.headless:
            self.game_state.modify_caption("Bot #" + str(self.bot.bot_num) + " is searching for " + self.mouse.type)
        
        # Main game loop until the bot catches the mouse or the game is interrupted
        while running and not exit_event.is_set():
            debug_print(f"Step {self.step_counter + 1}")
            
            if not self.headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        debug_print("Received quit event")
                        return "Game quit", self.step_counter
                    
            ship_state = self.game_state.get_ship_state_matrix()
            probabilities = self.bot.prob_model.get_probability_grid()
            bot_position = self.game_state.get_bot_state_matrix()

            debug_print("Bot action")
            new_bot_position = self.bot.action()
            
            bot_action = self.game_state.get_bot_action()
            
            # Store all states for this step
            self.states.append({
                'ship_layout': ship_state,
                'probability_matrix': probabilities,
                'bot_position': bot_position,
                'action': bot_action
            })

            # Check if the bot caught any mouse
            if isinstance(self.mouse, TwoStochasticMice): # Two mice
                self.mouse.catch_mouse(new_bot_position)
                if all(self.mouse.is_caught(i) for i in range(2)):
                    self.game_state.update_bot_position(new_bot_position)
                    if not self.headless:
                        pygame.display.update()
                        pygame.time.wait(self.delay)
                    self.write_states_to_csv()
                    return "Both intruders caught and released", self.step_counter + 1
            else: # One mouse
                if new_bot_position == self.mouse.get_position():
                    debug_print("Bot caught the mouse")
                    self.game_state.update_bot_position(new_bot_position)
                    if not self.headless:
                        pygame.display.update()
                        pygame.time.wait(self.delay)
                    self.write_states_to_csv()
                    return "Intruder caught and released", self.step_counter + 1

            # Update probabilities with new bot position
            self.game_state.update_bot_position(new_bot_position)

            # Move the mouse/mice
            debug_print("Mouse action")
            if isinstance(self.mouse, StationaryMouse):
                debug_print("STAY") 
            if isinstance(self.mouse, TwoStochasticMice): # Two mice
                old_mouse_positions = self.mouse.get_positions()
                self.mouse.move()
                new_mouse_positions = self.mouse.get_positions()
                self.game_state.mouse_positions = new_mouse_positions
                self.game_state.get_probability_model().update_on_mouse_move()
                self.game_state.update_mouse_positions(new_mouse_positions)
            else: # One mouse
                old_mouse_position = self.mouse.get_position()
                self.mouse.move()
                new_mouse_position = self.mouse.get_position()
                self.game_state.mouse_positions = [new_mouse_position]
                if isinstance(self.mouse, StochasticMouse):
                    self.game_state.get_probability_model().update_on_mouse_move()
                    self.game_state.update_mouse_positions([new_mouse_position])

            if not self.headless:
                debug_print("Updating display")
                self.game_state.draw_ship()
                self.game_state.draw_bot_and_mouse()
                pygame.display.update()
                pygame.time.wait(self.delay)
            
            self.step_counter += 1

        # Write states to CSV before returning
        self.write_states_to_csv()

        if exit_event.is_set():
            return "Game interrupted", self.step_counter

        return "Game ended unexpectedly", self.step_counter

    def write_states_to_csv(self):
        """Append all collected states to a single CSV file."""
        base_dir = os.path.join('data', 'tests')
        os.makedirs(base_dir, exist_ok=True)
        filename = os.path.join(base_dir, 'game_data.csv')

        file_exists = os.path.isfile(filename)

        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header only if the file is newly created
            if not file_exists:
                writer.writerow(['ship_layout', 'probability_matrix', 'bot_position', 'action'])
            
            for state in self.states:
                writer.writerow([
                    self.matrix_to_string(state['ship_layout']),
                    self.matrix_to_string(state['probability_matrix']),
                    self.matrix_to_string(state['bot_position']),
                    state['action']
                ])

    @staticmethod
    def matrix_to_string(matrix):
        """Convert a matrix to a string representation."""
        if isinstance(matrix, np.ndarray):
            return str(matrix.tolist())
        elif isinstance(matrix, list):
            return str(matrix)
        else:
            return str(matrix)
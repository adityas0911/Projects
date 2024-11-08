import pygame
import random as rd
import numpy as np
from transition.bayesian_network import ProbabilityModel
from transition.utils import debug_print, warning_print
from transition.mice import StationaryMouse, StochasticMouse, TwoStochasticMice

class Task:
    """
    Represents a single game task, managing the interaction between the bot and the mice.

    This class handles the game loop, including bot and mouse movements, and determines the outcome of the game.
    """

    def __init__(self, game_state, bot_class, mouse_class, alpha, delay=500, headless=False):
        """
        Initialize a Task object.

        Args:
            game_state (GameState): The current state of the game.
            bot_class (class): The class of the bot to be used in this task.
            mouse_class (class): The class of the mouse/mice to be used in this task.
            alpha (float): The sensitivity parameter for the bot's sensor.
            delay (int, optional): The delay between game steps in milliseconds. Defaults to 500.
            headless (bool, optional): Whether to run the game without GUI. Defaults to False.
        """
        self.game_state = game_state
        self.bot = bot_class(game_state, alpha)
        self.alpha = alpha
        self.step_counter = 0
        self.delay = delay
        self.headless = headless

        # Initialize mice
        if issubclass(mouse_class, TwoStochasticMice):
            self.mouse = mouse_class(game_state.mouse_positions, game_state)
        else:
            self.mouse = mouse_class(game_state.mouse_positions[0], game_state)

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
        
        if not self.headless:
            self.game_state.modify_caption("Bot #" + str(self.bot.bot_num) + " is searching for " + self.mouse.type)
        
        # Main game loop until the bot catches the mouse or the game is interrupted
        while running and not exit_event.is_set():
            debug_print(f"Step {self.step_counter}")
            
            if not self.headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        debug_print("Received quit event")
                        return "Game quit", self.step_counter

            debug_print("Bot deciding move")
            new_bot_position = self.bot.move()
            debug_print(f"Bot decided to move to {new_bot_position}")

            # Check if the bot caught any mouse
            if isinstance(self.mouse, TwoStochasticMice): # Two mice
                self.mouse.catch_mouse(new_bot_position)
                if all(self.mouse.is_caught(i) for i in range(2)):
                    self.game_state.update_bot_position(new_bot_position)
                    if not self.headless:
                        pygame.display.update()
                        pygame.time.wait(self.delay)
                    return "Both intruders caught and released", self.step_counter + 1
            else: # One mouse
                if new_bot_position == self.mouse.get_position():
                    debug_print("Bot caught the mouse")
                    self.game_state.update_bot_position(new_bot_position)
                    if not self.headless:
                        pygame.display.update()
                        pygame.time.wait(self.delay)
                    return "Intruder caught and released", self.step_counter + 1

            # Update probabilities with new bot position
            debug_print("Updating game state")
            self.game_state.update_bot_position(new_bot_position)

            # Move the mouse/mice
            debug_print("Moving mouse")
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

        # Check if the game was interrupted
        if exit_event.is_set():
            return "Game interrupted", self.step_counter

        return "Game ended unexpectedly", self.step_counter
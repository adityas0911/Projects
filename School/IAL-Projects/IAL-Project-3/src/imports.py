"""
Imports for simulation to not clutter the main file.
"""
import sys
import os

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'c_extensions')))

from ship.layout import ShipLayout
from ship.state import GameState
from transition.task import Task
from .bots.bot_test import BotTester
from .bots.bots import Bot1, Bot2, Bot3
from transition.mice import StationaryMouse, StochasticMouse, TwoStochasticMice
from transition.utils import debug_print, info_print, warning_print, error_print, exception_print, setup_logger, validate_parameters, add_logging_arguments, add_testing_arguments, add_simulation_arguments, setup_logging_from_args, delete_pycache
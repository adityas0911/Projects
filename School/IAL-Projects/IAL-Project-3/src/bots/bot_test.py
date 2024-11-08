import signal
from contextlib import contextmanager
import time
import numpy as np
from multiprocessing import Pool, Event
from functools import partial

from ship.state import GameState
from transition.task import Task
from transition.utils import info_print, debug_print, error_print, warning_print
from tqdm import tqdm

class TimeoutException(Exception):
    """Custom exception class for handling timeouts."""
    pass

@contextmanager
def timeout(seconds):
    """
    Context manager for setting a timeout on a block of code.

    Args:
        seconds (int): The number of seconds before timing out.

    Raises:
        TimeoutException: If the code block doesn't complete within the specified time.
    """
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

class BotTester:
    """
    A class for testing different bot implementations against various mouse types, can run single tests or multiple tests in parallel. Class is set up to used pool of workers for parallel execution and to handle timeouts for individual tests as well as keyboard interrupts.
    """
    
    def __init__(self, bot_classes, mouse_classes, initial_layout, display_dimension, alpha, num_tests, headless, fixed_positions, test_timeout=1200, exit_event=None):
        """
        Initialize the BotTester.

        Args:
            bot_classes (dict): Dictionary of bot classes to test.
            mouse_classes (dict): Dictionary of mouse classes to test against.
            initial_layout (list): The initial layout of the ship.
            display_dimension (int): The dimension of the display.
            alpha (float): The sensitivity parameter for the bot's sensor.
            num_tests (int): The number of tests to run for each bot-mouse combination.
            headless (bool): Whether to run the tests in headless mode.
            fixed_positions (tuple): Fixed starting positions for bot and mice.
            test_timeout (int, optional): Timeout for each individual test in seconds. Defaults to 300.
        """
        self.bot_classes = bot_classes
        self.mouse_classes = mouse_classes
        self.initial_layout = initial_layout
        self.display_dimension = display_dimension
        self.alpha = alpha
        self.num_tests = num_tests
        self.headless = headless
        self.fixed_positions = fixed_positions
        self.bot_position, self.mouse_positions = fixed_positions
        self.test_timeout = test_timeout
        self.exit_event = exit_event if exit_event is not None else Event()
        debug_print(f"BotTester initialized with {len(bot_classes)} bots, {len(mouse_classes)} mouse types, alpha={alpha}, num_tests={num_tests}")
        
    @staticmethod
    def init_worker():
        """
        Initialize the worker process to ignore SIGINT signals.
        """
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def __enter__(self):
        """
        Enter the context manager for handling pool of workers.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and clean up resources.
        """
        pass

    def run_single_test(self, bot_class, mouse_class):
        """
        Run a single test for a given bot-mouse combination.

        Args:
            bot_class: The bot class to test.
            mouse_class: The mouse class to test against.

        Returns:
            tuple: A tuple containing the outcome, number of steps, and elapsed time of the test.
        """
        if self.exit_event.is_set():
            return "Interrupted", 0, 0
        try:
            with timeout(self.test_timeout):
                mouse_name = mouse_class.__name__ if hasattr(mouse_class, '__name__') else str(mouse_class)
                debug_print(f"Starting single test with bot {bot_class.__name__} and mouse {mouse_name}")
                start_time = time.time()
                game_state = GameState(display_dimension=self.display_dimension, ship_layout=self.initial_layout, headless=self.headless,
                bot_position=self.fixed_positions[0],
                mouse_positions=self.fixed_positions[1])
                bot_instance = bot_class(game_state, self.alpha)
                if mouse_class.__name__ == 'TwoStochasticMice':
                    mouse_instance = mouse_class(game_state.mouse_positions, game_state)
                else:
                    mouse_instance = mouse_class(game_state.mouse_positions[0], game_state)
                task = Task(game_state, bot_instance, mouse_instance, self.alpha, headless=self.headless)
                outcome, steps = task.run(self.exit_event)
                elapsed_time = time.time() - start_time
                debug_print(f"Single test completed: outcome={outcome}, steps={steps}, time={elapsed_time:.2f}s")
                return outcome, steps, elapsed_time
        except TimeoutException:
            warning_print(f"Timeout occurred for a single test. Recording as timeout.")
            return "Timeout", self.test_timeout, self.test_timeout
        except Exception as e:
            error_print(f"Error in single test: {str(e)}")
            import traceback
            error_print(traceback.format_exc())
            return "Error", 0, 0
        
    def run_tests_sequentially(self):
        """
        Run tests sequentially for all bot-mouse combinations.

        Returns:
            dict: A dictionary containing the results for each bot-mouse combination.
        """
        results = {}
        try:
            for bot_id, bot_class in self.bot_classes.items():
                if self.exit_event.is_set():
                    break
                info_print(f"\nRunning tests for Bot {bot_id}")
                bot_results = {}
                for mouse_name, mouse_class in self.mouse_classes.items():
                    description = f"Bot {bot_id} vs {mouse_name} - alpha: {self.alpha:.2f}"
                    padded_description = f"{description:<50}"
                    info_print(f"Testing against {mouse_name}")
                    test_results = []
                    for _ in tqdm(range(self.num_tests), desc=padded_description, ncols=100):
                        if self.exit_event.is_set():
                            break
                        try:
                            with timeout(self.test_timeout):
                                outcome, steps, elapsed_time = self.run_single_test(bot_class, mouse_class)
                            test_results.append((outcome, steps, elapsed_time))
                        except TimeoutException:
                            warning_print(f"Timeout occurred for a single test. Recording as timeout.")
                            test_results.append(("Timeout", self.test_timeout, self.test_timeout))
                        except KeyboardInterrupt:
                            warning_print("\nTest interrupted by user. Saving partial results.")
                            self.exit_event.set()
                            break
                    bot_results[mouse_name] = self.process_results(test_results)
                results[bot_id] = bot_results
        except KeyboardInterrupt:
            warning_print("\nKeyboard interrupt detected. Exiting gracefully...")
            self.exit_event.set()
        return results

    def run_tests_parallel(self):
        """
        Run tests in parallel for all bot-mouse combinations.

        Returns:
            dict: A dictionary containing the results for each bot-mouse combination.
        """
        results = {}
        with Pool(initializer=self.init_worker) as pool:
            try:
                for bot_id, bot_class in self.bot_classes.items():
                    if self.exit_event.is_set():
                        break
                    info_print(f"\nRunning tests for Bot {bot_id}")
                    bot_results = {}
                    for mouse_name, mouse_class in self.mouse_classes.items():
                        description = f"Bot {bot_id} vs {mouse_name} - alpha: {self.alpha:.2f}"
                        padded_description = f"{description:<33}"
                        info_print(f"Testing against {mouse_name}")
                        
                        test_func = partial(self.run_single_test, bot_class, mouse_class)
                        test_results = []
                        for _ in tqdm(range(self.num_tests), desc=padded_description, ncols=100):
                            if self.exit_event.is_set():
                                break
                            try:
                                with timeout(self.test_timeout):
                                    result = pool.apply_async(test_func).get(timeout=self.test_timeout)
                                test_results.append(result)
                            except TimeoutException:
                                warning_print(f"Timeout occurred for a single test. Recording as timeout.")
                                test_results.append(("Timeout", self.test_timeout, self.test_timeout))
                        bot_results[mouse_name] = self.process_results(test_results)
                    results[bot_id] = bot_results
            except KeyboardInterrupt:
                warning_print("\nKeyboard interrupt detected. Exiting gracefully...")
                self.exit_event.set()
            except Exception as e:
                error_print(f"An error occurred: {str(e)}")
                self.exit_event.set()
            finally:
                pool.close()
                pool.join()
        return results

    def process_results(self, test_results):
        """
        Process the results of a series of tests.

        Args:
            test_results (list): A list of tuples containing the outcomes, steps, and times of each test.

        Returns:
            dict: A dictionary containing processed statistics from the test results.
        """
        # Set up default values
        total_games = len(test_results)
        if total_games == 0:
            warning_print("No test results to process")
            return self.create_empty_result()
        outcome_counts = {
            "Intruder caught and released": 0,
            "Both intruders caught and released": 0,
            "Game quit": 0,
            "Error": 0,
            "Timeout": 0
        }
        total_steps = 0
        all_steps = []
        total_time = 0
        all_times = []
        
        # Process test results, extracting relevant information
        for outcome, steps, elapsed_time in test_results:
            if outcome in outcome_counts:
                outcome_counts[outcome] += 1
            else:
                outcome_counts["Error"] += 1
            total_steps += steps
            all_steps.append(steps)
            total_time += elapsed_time
            all_times.append(elapsed_time)
        mice_caught = outcome_counts["Intruder caught and released"] + outcome_counts["Both intruders caught and released"]
        
        # Calculate statistics and set up result dictionary
        result = {
            'total_steps': total_steps,
            'total_games': total_games,
            'one_mouse_caught_count': outcome_counts["Intruder caught and released"],
            'both_mice_caught_count': outcome_counts["Both intruders caught and released"],
            'quit_count': outcome_counts["Game quit"],
            'unexpected_count': outcome_counts["Error"],
            'timeout_count': outcome_counts["Timeout"],
            'mice_caught': mice_caught,
            'average_steps': total_steps / total_games if total_games > 0 else float('nan'),
            'success_rate': (mice_caught / total_games * 100) if total_games > 0 else 0,
            'median_steps': np.median(all_steps) if all_steps else float('nan'),
            'max_steps': max(all_steps) if all_steps else float('nan'),
            'total_time': total_time,
            'average_time': total_time / total_games if total_games > 0 else float('nan'),
            'median_time': np.median(all_times) if all_times else float('nan'),
            'max_time': max(all_times) if all_times else float('nan')
        }
        debug_print(f"Processed results: {result}")
        return result

    def create_empty_result(self):
        """
        Create an empty result dictionary with default values for missing data or errors.

        Returns:
            dict: An empty result dictionary.
        """
        empty_result = {
            'total_steps': 0,
            'total_games': 0,
            'one_mouse_caught_count': 0,
            'both_mice_caught_count': 0,
            'quit_count': 0,
            'unexpected_count': 0,
            'timeout_count': 0,
            'mice_caught': 0,
            'average_steps': float('nan'),
            'success_rate': 0,
            'median_steps': float('nan'),
            'max_steps': float('nan'),
            'total_time': 0,
            'average_time': float('nan'),
            'median_time': float('nan'),
            'max_time': float('nan')
        }
        debug_print(f"Created empty result: {empty_result}")
        return empty_result

    def print_simulation_parameters(self, args, fixed_positions):
        """
        Print the simulation parameters.

        Args:
            args (argparse.Namespace): The parsed command-line arguments.
            fixed_positions (tuple): The fixed starting positions for the bot and mice.
        """
        info_print(f"Simulation Parameters:")
        info_print(f"  Alpha: {args.alpha}")
        info_print(f"  Number of tests: {args.num_tests}")
        info_print(f"  Headless mode: {'On' if args.headless else 'Off'}")
        info_print(f"  Grid size: {args.grid_size if not args.testing else args.testing_grid_size}")
        info_print(f"  Display size: {args.display_size if not args.testing else args.testing_display_size}")
        info_print(f"  Testing mode: {'On' if args.testing else 'Off'}")
        info_print(f"  Parallel execution: {'On' if args.parallel else 'Off'}")
        info_print(f"Fixed Positions:")
        info_print(f"  Bot starting position: {fixed_positions[0]}")
    
        if isinstance(fixed_positions[1], tuple) and len(fixed_positions[1]) == 2:
            info_print(f"  Mouse starting positions: {fixed_positions[1][0]} and {fixed_positions[1][1]}")
        else:
            info_print(f"  Mouse starting position: {fixed_positions[1]}")
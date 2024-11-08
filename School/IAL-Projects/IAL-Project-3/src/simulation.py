import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
from scipy import stats # type: ignore
import plotly.graph_objects as go # type: ignore
import sys
import os
import argparse
import logging
import atexit
import multiprocessing
from multiprocessing import Manager
from contextlib import contextmanager
from argparse import Namespace
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Aggregated imports
from src.imports import (
    ShipLayout,
    BotTester,
    Bot1,
    Bot2,
    Bot3,
    StationaryMouse,
    StochasticMouse,
    TwoStochasticMice,
    info_print,
    debug_print,
    warning_print,
    error_print,
    validate_parameters,
    setup_logging_from_args,
    add_logging_arguments,
    add_testing_arguments,
    add_simulation_arguments,
    delete_pycache
)

def main():
    """
    Main function to run the Intruder Alert simulation.
    
    This function sets up the simulation parameters, runs the simulation for different
    bot types and mouse types, processes the results, and generates various plots and outputs.
    """
    parser = argparse.ArgumentParser(description="Run Intruder Alert simulation")
    add_logging_arguments(parser)
    add_testing_arguments(parser)
    add_simulation_arguments(parser)
    
    args = parser.parse_args()

    try:
        validate_parameters(args)
    except ValueError as e:
        error_print(f"Invalid parameter: {e}")
        sys.exit(1)

    if args.clean:
        cleanup_results()
        info_print("Cleaned up data/results, data/plots, and data/logs directories")

    # Set up logger
    logger = setup_logging_from_args(args)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ensure the 'data' directories exists
    os.makedirs('data/results', exist_ok=True)
    os.makedirs('data/plots', exist_ok=True)
    os.makedirs('data/logs', exist_ok=True)    
    
    # For testing purposes, reduce the grid size and display size
    if args.testing:
        D = args.testing_grid_size
        display_dimension = args.testing_display_size
    else:
        D = args.size
        display_dimension = args.size
    
    # Set simulation values from arguments
    num_boards = args.num_boards
    num_tests = args.num_tests
    alpha_start = args.alpha_start
    alpha_end = args.alpha_end
    alpha_increment = args.alpha_increment
    mouse_class = args.mouse_class

    exit_event = multiprocessing.Event()

    try:
        results_stationary, results_stochastic, results_two_stochastic = run_simulation(D, num_boards, num_tests, alpha_start, alpha_end, alpha_increment, exit_event, args.show_GUI, args.new_board, mouse_class)

        if exit_event.is_set():
            info_print("Simulation interrupted. Processing partial results.")

        debug_print(f"Results stationary: {results_stationary}")
        debug_print(f"Results stochastic: {results_stochastic}")
        debug_print(f"Results two stochastic: {results_two_stochastic}")

        if not validate_results(results_stationary):
            warning_print("Invalid results for stationary mouse")
        if not validate_results(results_stochastic):
            warning_print("Invalid results for stochastic mouse")
        if not validate_results(results_two_stochastic):
            warning_print("Invalid results for two stochastic mice")

        optimal_alpha_stationary = find_optimal_alpha(results_stationary)
        if optimal_alpha_stationary is not None:
            info_print(f"Optimal alpha for stationary mouse: {optimal_alpha_stationary}")
        else:
            info_print("No valid results for stationary mouse.")

        optimal_alpha_stochastic = find_optimal_alpha(results_stochastic)
        if optimal_alpha_stochastic is not None:
            info_print(f"Optimal alpha for stochastic mouse: {optimal_alpha_stochastic}")
        else:
            info_print("No valid results for stochastic mouse.")

        optimal_alpha_two_stochastic = find_optimal_alpha(results_two_stochastic)
        if optimal_alpha_two_stochastic is not None:
            info_print(f"Optimal alpha for two stochastic mice: {optimal_alpha_two_stochastic}")
        else:
            info_print("No valid results for two stochastic mice.")
        
        info_print("Writing results to file")
        results_string = write_and_print_results(results_stationary, results_stochastic, results_two_stochastic, f'simulation_results_{timestamp}.txt')
    
        info_print("Simulation Results:")
        print(results_string)
        
        info_print("Plotting results")
        # plot_results(results_stationary, "Stationary Mouse vs Bots", f"stationary_vs_bots_{timestamp}.png")
        # plot_results(results_stochastic, "Moving Mouse vs Bots", f"stochastic_vs_bots_{timestamp}.png")
        # plot_results(results_two_stochastic, "Two Mice vs Bots", f"two_stochastic_vs_bots_{timestamp}.png")

        plot_bot_comparison(results_stationary, "Stationary", f"stationary_comparison_{timestamp}.png")
        plot_bot_comparison(results_stochastic, "Stochastic", f"stochastic_comparison_{timestamp}.png")
        plot_bot_comparison(results_two_stochastic, "TwoStochastic", f"two_stochastic_comparison_{timestamp}.png")
    
    except KeyboardInterrupt:
        warning_print("\nKeyboard interrupt detected. Exiting gracefully...")
        exit_event.set()
    except Exception as e:
        error_print(f"An unexpected error occurred: {str(e)}")
    finally:
        cleanup()

def run_simulation(size, num_boards, num_tests, alpha_start, alpha_end, alpha_increment, exit_event, show_GUI, new_board, mouse_class):
    """
    Run the simulation for different bot types and mouse types.

    Args:
        size (int): The size of the game board.
        num_boards (int): The number of different board layouts to test.
        num_tests (int): The number of tests to run for each configuration.
        alpha_start (float): The starting value for the alpha parameter.
        alpha_end (float): The ending value for the alpha parameter.
        alpha_increment (float): The increment for the alpha parameter.
        exit_event (multiprocessing.Event): Event to signal when the simulation should exit.
        show_GUI (bool): Whether to show the GUI during simulation.

    Returns:
        tuple: Three lists containing results for stationary, stochastic, and two stochastic mice.
    """
    debug_print(f"Starting simulation with {num_boards} boards, {num_tests} tests, alpha range: {alpha_start}-{alpha_end}")
    alpha_values = np.arange(alpha_start, alpha_end, alpha_increment)
    
    bot_classes = {3: Bot3}
    
    if mouse_class == 0:
        mouse_classes = {"Stationary": StationaryMouse}
    elif mouse_class == 1:
        mouse_classes = {"Stochastic": StochasticMouse}

    results_stationary = []
    results_stochastic = []
    results_two_stochastic = []

    with Manager() as manager:
        shared_exit_event = manager.Event()

        try:
            for alpha in alpha_values:
                if shared_exit_event.is_set():
                    break
                debug_print(f"Running tests for alpha = {alpha}")
                for board_num in range(num_boards):
                    if shared_exit_event.is_set():
                        break
                    
                    board_file = f'board_size_{size}.json'

                    if os.path.exists(board_file) and not new_board:
                        debug_print(f"Loading existing board from {board_file}")
                        ship_layout = ShipLayout.load_from_file(board_file)
                        initial_layout = ship_layout.get_layout()
                        fixed_positions = ship_layout.get_fixed_starting_positions()
                    else:
                        debug_print(f"Creating new board and saving to {board_file}")
                        ship_layout = ShipLayout(D=size)
                        initial_layout = ship_layout.get_layout()
                        ship_layout.generate_starting_positions()
                        fixed_positions = ship_layout.get_fixed_starting_positions()
                        ship_layout.save_to_file(board_file)
                    
                    # Create the args Namespace object
                    args = Namespace(
                        alpha=alpha,
                        num_tests=num_tests,
                        headless=not show_GUI,
                        grid_size=size,
                        display_size=size,
                        testing=False,
                        parallel=True,
                        testing_grid_size=size,
                        testing_display_size=size
                    )

                    with BotTester(
                        bot_classes=bot_classes,
                        mouse_classes=mouse_classes,
                        initial_layout=initial_layout,
                        display_dimension=size,
                        alpha=alpha,
                        num_tests=num_tests,
                        headless=not show_GUI,
                        fixed_positions=fixed_positions,
                        exit_event=shared_exit_event
                    ) as bot_tester:
                        bot_tester.print_simulation_parameters(args, fixed_positions)
                        try:
                            debug_print("Running tests for current board")
                            results = bot_tester.run_tests_parallel()
                            debug_print(f"Results for current board: {results}")
                            
                            # Append results for each mouse type and each bot
                            for bot_id, bot_results in results.items():
                                results_stationary.append((alpha, size, {**bot_results['Stationary'], 'bot_id': bot_id}))
                                results_stochastic.append((alpha, size, {**bot_results['Stochastic'], 'bot_id': bot_id}))
                                results_two_stochastic.append((alpha, size, {**bot_results['TwoStochas'], 'bot_id': bot_id}))
                            
                        except KeyboardInterrupt:
                            warning_print("Keyboard interrupt detected. Exiting simulation...")
                            shared_exit_event.set()
                            break
                        except Exception as e:
                            error_print(f"Error running tests: {str(e)}")
                            continue
                if shared_exit_event.is_set():
                    break
        except KeyboardInterrupt:
            warning_print("Keyboard interrupt detected. Exiting simulation...")
            shared_exit_event.set()
        except Exception as e:
            error_print(f"Error in simulation: {str(e)}")

    debug_print(f"Simulation completed. Results: Stationary: {len(results_stationary)}, Stochastic: {len(results_stochastic)}, Two Stochastic: {len(results_two_stochastic)}")
    
    return results_stationary, results_stochastic, results_two_stochastic

def calculate_ci(data, confidence=0.95):
    """
    Calculate the confidence interval for a given dataset.

    Args:
        data (list): The dataset to calculate the confidence interval for.
        confidence (float): The confidence level (default is 0.95 for 95% CI).

    Returns:
        tuple: The lower and upper bounds of the confidence interval.
    """
    if len(data) < 2:
        return np.nan, np.nan
    mean, sem = np.mean(data), stats.sem(data)
    return stats.t.interval(confidence, len(data)-1, loc=mean, scale=sem)

def plot_results(results, title, filename):
    """
    Plot the results of the simulation.

    Args:
        results (list): The results to plot.
        title (str): The title of the plot.
        filename (str): The filename to save the plot as.
    """
    alphas = sorted(set([r[0] for r in results]))
    data = np.zeros(len(alphas))

    for alpha, _, res in results:
        alpha_idx = alphas.index(alpha)
        data[alpha_idx] = res.get('average_steps', 0)  # Use 0 if 'average_steps' is not present

    if np.all(data == 0):
        warning_print(f"No valid data to plot for {title}")
        return

    ci_low, ci_high = calculate_ci(data[data != 0])

    plt.figure(figsize=(10, 6))
    plt.plot(alphas, data, label='Average Steps')
    if not np.isnan(ci_low) and not np.isnan(ci_high):
        plt.fill_between(alphas, ci_low, ci_high, color='b', alpha=0.1)
    plt.xlabel('Alpha')
    plt.ylabel('Average Steps')
    plt.title(title)
    plt.legend()
    plt.savefig(os.path.join('data', 'plots', filename))
    plt.close()

def plot_bot_comparison(results, mouse_type, filename):
    """
    Plot a comparison of different bot performances.

    Args:
        results (list): The results to plot.
        mouse_type (str): The type of mouse used in the simulation.
        filename (str): The filename to save the plot as.
    """
    alphas = sorted(set([r[0] for r in results]))
    plt.figure(figsize=(12, 6))
    
    debug_print(f"Plotting comparison for {mouse_type} mouse")
    debug_print(f"Alpha values: {', '.join([f'{alpha:.3f}' for alpha in alphas])}")
    
    for bot_id in [1, 2, 3]:
        # Filter and group data for the current bot
        bot_data = {}
        for alpha, _, res in results:
            if isinstance(res, dict) and 'average_steps' in res and res.get('bot_id') == bot_id:
                if alpha not in bot_data:
                    bot_data[alpha] = []
                bot_data[alpha].append(res['average_steps'])
        
        # Calculate average steps for each alpha
        average_steps = [np.mean(bot_data.get(alpha, [np.nan])) for alpha in alphas]
        
        debug_print(f"Bot {bot_id} data:")
        debug_print(f"  Number of alpha values: {len(bot_data)}")
        debug_print("  Average steps:")
        for alpha, avg_step in zip(alphas, average_steps):
            debug_print(f"    Alpha {alpha:.3f}: {avg_step:.2f}")
        
        if not all(np.isnan(step) for step in average_steps):
            plt.plot(alphas, average_steps, label=f'Bot {bot_id}')
        else:
            warning_print(f"No valid data available for Bot {bot_id}")
    
    plt.xlabel('Alpha')
    plt.ylabel('Average Steps')
    plt.title(f'Bot Performance Comparison - {mouse_type} Mouse')
    plt.legend()
    plt.savefig(os.path.join('data', 'plots', filename))
    plt.close()
    
def find_optimal_alpha(results, metric='success_rate'):
    """
    Find the optimal alpha value based on a given metric.

    Args:
        results (list): The results to analyze.
        metric (str): The metric to optimize for (default is 'success_rate').

    Returns:
        float: The optimal alpha value, or None if no valid results.
    """
    valid_results = [r for r in results if metric in r[2]]
    if not valid_results:
        return None
    best_alpha = max(valid_results, key=lambda r: r[2][metric])[0]
    return best_alpha

def validate_results(results):
    """
    Validate the simulation results.

    Args:
        results (list): The results to validate.

    Returns:
        bool: True if results are valid, False otherwise.
    """
    if not results:
        debug_print("Results are empty")
        return False
    
    debug_print(f"Validating results: {results}")
    
    for item in results:
        if not isinstance(item, tuple) or len(item) != 3:
            debug_print(f"Invalid item in results: {item}")
            return False
        
        alpha, size, res = item
        debug_print(f"Validating results for alpha={alpha}, size={size}")
        
        if not isinstance(res, dict):
            debug_print(f"Expected dictionary for results, got {type(res)}")
            return False
        
        if 'success_rate' not in res:
            debug_print(f"Missing 'success_rate' in results")
            return False
        
        debug_print(f"Success rate: {res['success_rate']}")
    
    return True

def write_and_print_results(results_stationary, results_stochastic, results_two_stochastic, filename):
    """
    Write the simulation results to a file and return them as a string to be printed to the console.

    Args:
        results_stationary (list): Results for stationary mouse.
        results_stochastic (list): Results for stochastic mouse.
        results_two_stochastic (list): Results for two stochastic mice.
        filename (str): The filename to save the results as.

    Returns:
        str: A string representation of the results.
    """
    def write_and_print(file, line):
        """
        Write a line to a file and print it to the console.
        
        Args:
            file (file): The file object to write to.
            line (str): The line to write and print.
        """
        file.write(line + '\n')
        info_print(line)

    def format_value(value):
        """
        Format a value as a string.
        
        Args:
            value: The value to format.
            
        Returns:
            str: The formatted value.
        """
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)

    output = []
    output.append("=== Simulation Results ===")
    output.append("")

    with open(os.path.join('data/results', filename), 'w') as f:
        for mouse_type, results in [("Stationary", results_stationary), 
                                    ("Stochastic", results_stochastic), 
                                    ("Two Stochastic", results_two_stochastic)]:
            output.append(f"{mouse_type} Mouse Results:")
            output.append("=" * (len(mouse_type) + 14))
            output.append("")

            # Group results by alpha
            alpha_results = {}
            for alpha, size, res in results:
                if alpha not in alpha_results:
                    alpha_results[alpha] = []
                alpha_results[alpha].append((size, res))

            optimal_alpha = find_optimal_alpha(results)
            output.append(f"Optimal Alpha: {optimal_alpha:.5f}")
            output.append("")

            # Loop through each alpha value
            for alpha, alpha_tests in alpha_results.items():
                output.append(f"Alpha: {alpha:.5f}")
                output.append("-" * 40)

                overall_totals = {bot_id: {'total_steps': 0, 'total_games': 0, 'max_steps': 0, 'total_time': 0, 'max_time': 0, 
                                           'mice_caught': 0, 'one_mouse_caught_count': 0, 'both_mice_caught_count': 0, 
                                           'quit_count': 0, 'unexpected_count': 0} 
                                  for bot_id in range(1, 4)}  # Assuming 3 bots
                all_steps = {bot_id: [] for bot_id in range(1, 4)}
                all_times = {bot_id: [] for bot_id in range(1, 4)}

                # Loop through each board size
                for size, res in alpha_tests:
                    bot_id = res['bot_id']
                    overall_totals[bot_id]['total_steps'] += res['total_steps']
                    overall_totals[bot_id]['total_games'] += res['total_games']
                    overall_totals[bot_id]['max_steps'] = max(overall_totals[bot_id]['max_steps'], res['max_steps'])
                    overall_totals[bot_id]['total_time'] += res['total_time']
                    overall_totals[bot_id]['max_time'] = max(overall_totals[bot_id]['max_time'], res['max_time'])
                    overall_totals[bot_id]['mice_caught'] += res['mice_caught']
                    overall_totals[bot_id]['one_mouse_caught_count'] += res['one_mouse_caught_count']
                    overall_totals[bot_id]['both_mice_caught_count'] += res['both_mice_caught_count']
                    overall_totals[bot_id]['quit_count'] += res['quit_count']
                    overall_totals[bot_id]['unexpected_count'] += res['unexpected_count']
                    all_steps[bot_id].extend([res['average_steps']] * res['total_games'])
                    all_times[bot_id].extend([res['average_time']] * res['total_games']) 

                # Calculate results for each bot
                for bot_id, totals in overall_totals.items():
                    output.append(f"Bot {bot_id}:")
                    output.append("-" * (len(str(bot_id)) + 5))
                    
                    avg_steps = totals['total_steps'] / totals['total_games'] if totals['total_games'] > 0 else 0
                    median_steps = np.median(all_steps[bot_id]) if all_steps[bot_id] else 0
                    avg_time = totals['total_time'] / totals['total_games'] if totals['total_games'] > 0 else 0
                    median_time = np.median(all_times[bot_id]) if all_times[bot_id] else 0
                    success_rate = (totals['mice_caught'] / totals['total_games'] * 100) if totals['total_games'] > 0 else 0

                    output.append(f"  Total Steps               {totals['total_steps']}")
                    output.append(f"  Average Steps             {avg_steps:.0f}")
                    output.append(f"  Median Steps              {median_steps:.0f}")
                    output.append(f"  Max Steps                 {totals['max_steps']}")
                    output.append(f"  Total Time                {totals['total_time']:.2f}")
                    output.append(f"  Average Time              {avg_time:.2f}")
                    output.append(f"  Median Time               {median_time:.2f}")
                    output.append(f"  Max Time                  {totals['max_time']:.2f}")
                    output.append(f"  Total Games               {totals['total_games']}")
                    output.append(f"  Success Rate              {success_rate:.2f}%")
                    output.append(f"  One Mouse Caught          {totals['one_mouse_caught_count']}")
                    output.append(f"  Both Mice Caught          {totals['both_mice_caught_count']}")
                    output.append(f"  Total Mice Caught         {totals['mice_caught']}")
                    output.append(f"  Quit Count                {totals['quit_count']}")
                    output.append(f"  Unexpected Count          {totals['unexpected_count']}")
                    output.append("")

                output.append("")

            output.append("")

        # Write all output to file
        f.write('\n'.join(output))

    # Return the output as a string
    return '\n'.join(output)

@contextmanager
def redirect_output():
    """
    Context manager to temporarily redirect stdout and stderr to devnull.

    This is used for suppressing output during keyboard interrupt handling.
    """
    try:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        devnull = open(os.devnull, 'w')
        sys.stdout, sys.stderr = devnull, devnull
        yield
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        devnull.close()

def cleanup():
    """
    Cleanup operations to be performed before exiting the program on keyboard interrupt.
    """
    with redirect_output():
        # Add any cleanup operations here
        pass
    
def cleanup_results():
    """
    Clean up the results, plots, and logs directories.
    """
    directories_to_clean = ['data/logs', 'data/plots', 'data/results']

    for directory in directories_to_clean:
        try:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        try:
                            os.unlink(file_path)
                        except Exception as e:
                            error_print(f"Failed to delete {file_path}. Reason: {str(e)}")
            else:
                os.makedirs(directory)
        except Exception as e:
            error_print(f"Failed to clean {directory}. Reason: {str(e)}")

    # Ensure all directories exist
    for directory in directories_to_clean:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    """
    Run the main function when the script is executed and delete __pycache__ folders on exit.
    """
    main()
    atexit.register(lambda: delete_pycache(['./src','./src/bots', './src/ship', './src/transition']))
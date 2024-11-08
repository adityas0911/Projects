import os
import shutil
import logging
import argparse
from datetime import datetime

def setup_logger(log_level=logging.INFO, log_to_file=False, log_to_console=True):
    logger = logging.getLogger('')
    logger.setLevel(log_level)
    
    # Remove all existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create a custom formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    if log_to_file:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_dir = os.path.join(project_root, 'data', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"simulation_{timestamp}.log")
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def debug_print(*args, **kwargs):
    """
    Print a debug message using the logger.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    logging.debug(' '.join(map(str, args)), **kwargs)

def info_print(*args, **kwargs):
    """
    Print an info message using the logger.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    logging.info(' '.join(map(str, args)), **kwargs)

def warning_print(*args, **kwargs):
    """
    Print a warning message using the logger.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    logging.warning(' '.join(map(str, args)), **kwargs)
    
def error_print(*args, **kwargs):
    """
    Print an error message using the logger.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    logging.error(' '.join(map(str, args)), **kwargs)
    
def exception_print(*args, **kwargs):
    """
    Print an exception message using the logger.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    logging.exception(' '.join(map(str, args)), **kwargs)

def delete_pycache(directories):
    """
    Delete __pycache__ folders in the specified directories.

    Args:
        directories (list): List of directory paths to search for __pycache__ folders.
    """
    try:
        for directory in directories:
            pycache_path = os.path.join(directory, '__pycache__')
            if os.path.exists(pycache_path):
                shutil.rmtree(pycache_path)
                debug_print(f"Deleted {pycache_path}.")
            else:
                debug_print(f"{pycache_path} was not found.")
    except Exception as e:
        debug_print(f"Error deleting __pycache__ folders: {e}.")

def validate_parameters(args):
    """
    Validate the command-line arguments.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

    Raises:
        ValueError: If any of the parameters are invalid.
    """
    if args.num_tests <= 0:
        raise ValueError("Number of tests must be greater than 0")
    if args.testing and (args.testing_grid_size <= 0 or args.testing_display_size <= 0):
        raise ValueError("Testing grid size and display size must be greater than 0")
    
    # Validate simulation arguments
    if args.size <= 0:
        raise ValueError("Board size must be greater than 0")
    if args.num_boards <= 0:
        raise ValueError("Number of boards must be greater than 0")
    if args.alpha_start < 0 or args.alpha_start > 1:
        raise ValueError("Alpha start must be between 0 and 1")
    if args.alpha_end < 0 or args.alpha_end > 1:
        raise ValueError("Alpha end must be between 0 and 1")
    if args.alpha_start >= args.alpha_end:
        raise ValueError("Alpha start must be less than alpha end")
    if args.alpha_increment <= 0:
        raise ValueError("Alpha increment must be greater than 0")
    
def setup_logging_from_args(args):
    """
    Set up logging based on command-line arguments.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

    Returns:
        logging.Logger: The configured logger object.
    """
    log_level = logging.DEBUG if args.debug else logging.INFO
    log_to_file = args.log_to_file
    log_to_console = not args.no_console_output
    return setup_logger(log_level, log_to_file, log_to_console)

def add_logging_arguments(parser):
    """
    Add logging-related arguments to the argument parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add arguments to.
    """
    parser.add_argument('--log-to-file', action='store_true', help="Log output to file")
    parser.add_argument('--no-console-output', action='store_true', help="Disable console output")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")

def add_testing_arguments(parser):
    """
    Add testing-related arguments to the argument parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add arguments to.
    """
    parser.add_argument('--testing', action='store_true', help="Enable testing mode with smaller grid size")
    parser.add_argument('--testing_grid_size', type=int, default=10, help="Grid size for testing mode")
    parser.add_argument('--testing_display_size', type=int, default=500, help="Display size for testing mode")
    
def add_simulation_arguments(parser):
    """
    Add simulation-related arguments to the argument parser.
    
    Args:
        parser (argparse.ArgumentParser): The argument parser to add arguments to.
    """
    parser.add_argument('--size', type=int, default=40, help='Fixed board size')
    parser.add_argument('--num_boards', type=int, default=5, help='Number of boards')
    parser.add_argument('--num_tests', type=int, default=5, help='Number of tests')
    parser.add_argument('--alpha_start', type=float, default=0.04999, help='Starting value of alpha')
    parser.add_argument('--alpha_end', type=float, default=0.59999, help='Ending value of alpha')
    parser.add_argument('--alpha_increment', type=float, default=0.05, help='Increment value of alpha')
    parser.add_argument('--clean', action='store_true', help='Clean up the data directory')
    parser.add_argument('--show_GUI', action='store_true', help='Show GUI')
    parser.add_argument('--new_board', action='store_true', help='Force generation of a new board')
    parser.add_argument('--mouse_class', type=int, default=0, help='Mouse class')

# Project 2 - Intruder Alert Simulation

This repository contains project 2 for the course 01:198:440:C1 INTRO ARTIFIC INTELL Summer 2024.

This project simulates a bot navigating through a spaceship to catch mice before they cause damage. The simulation includes different bot strategies and types of mice, allowing for performance comparison under various conditions.

## Course Information

- **Course:** [01:198:440:C1 INTRO ARTIFIC INTELL](https://rutgers.instructure.com/courses/281725)
- **Professor:** [Charles Wes Cowan](mailto:w.cowan@rutgers.edu)

## Due Date

- **July 08, 2024 @ 11:59 PM EDT**

## Contributor(s)

- **Aditya Sharma**

  - **RUID:** 219008361
  - **NetID:** as4108
  - **Email:** [as4108@scarletmail.rutgers.edu](mailto:as4108@scarletmail.rutgers.edu)

- **Alexander Laudino**

  - **RUID:** 024004315
  - **NetID:** asl172
  - **Email:** [asl172@scarletmail.rutgers.edu](mailto:asl172@scarletmail.rutgers.edu)

## Project Structure

- simulation.py: Handles the main simulation logic and data processing.
- bot_test.py: Executes single or parallel tests
- task.py: Executes tasks involving bot and mouse interactions.
- bayesian_network.py: Implements the probability model for the bot's decision-making.
- bots.py: Contains the bot strategies.
- mice.py: Defines the behavior of different types of mice.
- state.py: Manages the game state and visualization.
- layout.py: Creates and manages the ship layout.
- utils.py: Utility functions for logging, parameter validation, and result processing.

```bash
project_root/
├── README.md
├── data/
│   ├── logs/
│   ├── plots/
│   └── results/
├── requirements.txt
├── setup.py
└── src/
    ├── bots/
    │   ├── __init__.py
    │   ├── bot_test.py
    │   └── bots.py
    ├── imports.py
    ├── ship/
    │   ├── __init__.py
    │   ├── layout.py
    │   └── state.py
    ├── simulation.py
    └── transition/
        ├── __init__.py
        ├── bayesian_network.py
        ├── mice.py
        ├── task.py
        └── utils.py
```

## Setup

### Dependencies

- numpy
- matplotlib
- scipy
- plotly
- pygame
- tqdm
- kaleido

To install required Python Packages as listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Installation of Project

Project also provides a `setup.py` file to assist with installation of project. To install the project, please run from root directory:

```bash
pip install .
```

## Running the Simulation

1. **Unzip the Files**

   - Extract the contents of the zip folder.

2. **Run the simulation**

   - ```bash
      python3 src/simulation.py
     ```

      This will run the simulation starting at a given alpha and increment its value until reaching an ending alpha; default values for running simulation are:

      - Grid size = 40
      - Num of boards to test = 5
      - Num of tests per board = 5
      - Starting alpha = 0.09999
      - Ending alpha = 0.99999
      - Alpha increment = 0.1

### Command Line Arguments

- **Logging arguments:**
  - `--debug`: Enables advanced logging for debugging purposes
  - `--log-to-file`: Sets the output to be logged to a text file under `data/logs` directory
  - `--no-console-output`: Disables logging output to console

- **Testing Arguments:**
  - `--testing`: Enable running tests with a smaller grid size.
  - `--testing_grid_size`: Grid size for testing mode.
  - `--testing_display_size`: Display size for testing mode.

- **Simulation Arguments:**
  - `--size`: Size of board
  - `--num_boards`: Number of boards to test on.
  - `--num_tests`: Number of tests.
  - `--alpha_start`: Starting value of alpha.
  - `--alpha_end`: Ending value of alpha.
  - `--alpha_increment`: Increment value of alpha.
  - `--clean`: Clean up the data directory.
  - `--show_GUI`: Show GUI.

## Results and Analysis

The simulation outputs results to the data/results directory and generates plots in the data/plots directory.

### Viewing Results

You can view the detailed results and analysis in the console output or check the log files if logging to a file is enabled.

### Plotting Results

The simulation generates plots to visualize the performance of different bots against stationary and moving mice. These plots are saved in the data/plots directory.

## Contact Information

- For any questions or issues related to the project, please contact the contributor(s) via their provided emails.

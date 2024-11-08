import numpy as np

# Notation:

# 'B' = blocked
# 'O' = open
# 'F' = fire
# 'bot' = bot
# 'button' = button

def risk_map(ship_layout, fire_positions, q, steps): # Defines a function to calculate the risk map.
  D = len(ship_layout) # Defines the length of the ship layout.
  risk_map = np.zeros((D, D)) # Initializes a 2D array to keep track of the risk of each cell.
  neighboring_cells = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Initializes a list to keep track of the neighbors of each cell.

  for _ in range(steps): # For each step:
    new_fire_positions = set() # Initializes a set to keep track of the new fire positions.

    for row, column in fire_positions: # For each cell in the fire_positions set:
      for drow, dcolumn in neighboring_cells: # Checks all the neighbors of the current cell.
        new_row, new_column = row + drow, column + dcolumn # Calculates the neighbor's row and column.

        if (0 <= new_row < D and 0 <= new_column < D): # If the neighbor is within the grid:
          if (ship_layout[new_row][new_column] == 'O'): # If the neighbor is open:
            spread_probability = 1 - (1 - q) ** sum((new_row + ddrow, new_column + ddcolumn) in fire_positions for ddrow, ddcolumn in neighboring_cells) # Calculates the probability of spreading fire.
            risk_map[new_row][new_column] += spread_probability # Updates the risk of the neighbor.
            
            if np.random.rand() < spread_probability: # If the random number is less than the spread probability:
              new_fire_positions.add((new_row, new_column)) # Adds the neighbor to the new_fire_positions set.

    fire_positions.update(new_fire_positions) # Updates the fire_positions set.

  return risk_map # Returns the risk map.

import random as rd

# Notation:

# 'B' = blocked
# 'O' = open
# 'F' = fire
# 'bot' = bot
# 'button' = button

def fire_spread(ship_layout, q): # Defines a function to determine the cells that fire spread to.
  fire_spreads = [] # Initializes a list to store the positions where the fire can spread to.

  for row in range(len(ship_layout)): # Checks each row in the ship's interior.
    for column in range(len(ship_layout[0])): # Checks each column in each row.
      if ship_layout[row][column] in {'O', 'bot', 'button'}: # If the current cell is open, bot, or button:
        K = 0 # Initializes a variable to keep track of the count of burning neighbors.

        if (row > 0 and ship_layout[row - 1][column] == 'F'): # If the top adjacent cell within the ship is burning:
          K += 1 # Increments the count of burning neighbors.
        if (row < len(ship_layout) - 1 and ship_layout[row + 1][column] == 'F'): # If the bottom adjacent cell within the ship is burning:
          K += 1 # Increments the count of burning neighbors.
        if (column > 0 and ship_layout[row][column - 1] == 'F'): # If the left adjacent cell within the ship is burning:
          K += 1 # Increments the count of burning neighbors.
        if (column < len(ship_layout[0]) - 1 and ship_layout[row][column + 1] == 'F'): # If the right adjacent cell within the ship is burning:
          K += 1 # Increments the count of burning neighbors.

        fire_probability = 1 - (1 - q) ** K # Initializes a variable to keep track of the probability of the fire spreading to the adjacent cell.
        roll = rd.random() # Initializes a variable to keep track of the random number between 0 and 1.

        if roll < fire_probability: # If the random number is less than the probability of the fire spreading to the adjacent cell:
          fire_spreads.append((row, column)) # Add this cell to the list of fire spreads.

  return fire_spreads # Returns the list of cells that fire spread to.

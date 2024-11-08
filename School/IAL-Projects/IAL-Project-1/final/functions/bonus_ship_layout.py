import random as rd

# Notation:

# 'B' = blocked
# 'O' = open
# 'F' = fire
# 'bot' = bot
# 'button' = button

def bonus_ship_layout(D): # Defines a function to create the bonus ship's layout with dimensions D x D.

######################################################################################
##################################                  ##################################
################################## TO BE CONTINUED! ##################################
##################################                  ##################################
######################################################################################

  ship_layout = [['B' for _ in range(D)] for _ in range(D)] # Creates a 2D array representing the ship, initializing all cells as blocked.
  one_open_neighbor = [] # Initializes a list to keep track of blocked cells with exactly one open neighbor.
  dead_ends = [] # Initializes a list to keep track of open cells with exactly one open neighbor.
  closed_neighbors = {} # Initializes a dictionary to keep track of the cells that are closed neighbors.
  initial, cell = rd.randint(0, D - 1), rd.randint(0, D - 1) # Initializes the initial cell, which randomly selects coordinates within the interior of the grid.
  ship_layout[initial][cell] = 'O' # Marks the randomly chosen interior cell as open.

  while True: # Iteratively does the following:
    one_open_neighbor.clear() # Clears the one_open_neighbor list.

    for row in range(0, D - 1): # Checks each row in the ship's interior.
      for column in range(0, D - 1): # Checks each column in each row.
        if ship_layout[row][column] == 'B': # If the current cell is blocked:
          open_neighbors = 0 # Initializes a variable to keep track of the number of open neighbors adjacent to the current cell.

          if (row > 0 and ship_layout[row - 1][column] == 'O'): # If the top adjacent cell within the ship is open:
            open_neighbors += 1 # Increments the count of open neighbors.
          if (row < D - 1 and ship_layout[row + 1][column] == 'O'): # If the bottom adjacent cell within the ship is open:
            open_neighbors += 1 # Increments the count of open neighbors.
          if (column > 0 and ship_layout[row][column - 1] == 'O'): # If the left adjacent cell within the ship is open:
            open_neighbors += 1 # Increments the count of open neighbors.
          if (column < D - 1 and ship_layout[row][column + 1] == 'O'): # If the right adjacent cell within the ship is open:
            open_neighbors += 1 # Increments the count of open neighbors.
          if open_neighbors == 1: # If the count of open neighbors is exactly 1:
            one_open_neighbor.append((row, column)) # Adds the current cell to the one_open_neighbor list.

    if len(one_open_neighbor) == 0: # If the one_open_neighbor list is empty:
      break # Break out of the while loop.

    random, cell = one_open_neighbor[rd.randint(0, len(one_open_neighbor) - 1)] # Randomly selects one of the cells in the one_open_neighbor list.
    ship_layout[random][cell] = 'O' # Marks the selected cell as open.

  for row in range(0, D - 1): # Checks each row in the ship's interior.
    for column in range(0, D - 1): # Checks each column in each row.
      if ship_layout[row][column] == 'O': # If the current cell is open:
        blocked_neighbors = [] # Initializes a list to keep track of the cells that are blocked neighbors.
        open_neighbors = 0 # Initializes a variable to keep track of the number of open neighbors adjacent to the current cell.

        if row > 0: # If the current cell is not in the top edge of the grid:
          if ship_layout[row - 1][column] == 'O': # If the top adjacent cell is open:
            open_neighbors += 1 # Increments the count of open neighbors.
          else: # Else if the top adjacent cell is not open:
            blocked_neighbors.append((row - 1, column)) # Adds the top adjacent cell to the blocked_neighbors list.
        if row < D - 1: # If the current cell is not in the bottom edge of the grid:
          if ship_layout[row + 1][column] == 'O': # If the bottom adjacent cell is open:
            open_neighbors += 1 # Increments the count of open neighbors.
          else: # Else if the bottom adjacent cell is not open:
            blocked_neighbors.append((row + 1, column)) # Adds the bottom adjacent cell to the blocked_neighbors list.
        if column > 0: # If the current cell is not in the left edge of the grid:
          if ship_layout[row][column - 1] == 'O': # If the left adjacent cell is open:
            open_neighbors += 1 # Increments the count of open neighbors.
          else: # Else if the left adjacent cell is not open:
            blocked_neighbors.append((row, column - 1)) # Adds the left adjacent cell to the blocked_neighbors list.
        if column < D - 1: # If the current cell is not in the right edge of the grid:
          if ship_layout[row][column + 1] == 'O': # If the right adjacent cell is open:
            open_neighbors += 1 # Increments the count of open neighbors.
          else: # Else if the right adjacent cell is not open:
            blocked_neighbors.append((row, column + 1)) # Adds the right adjacent cell to the blocked_neighbors list.
        if open_neighbors == 1: # If the count of open neighbors is exactly 1:
          dead_ends.append((row, column)) # Adds the current cell to the dead_ends list.
          closed_neighbors[(row, column)] = closed_neighbors.get((row, column), []) + blocked_neighbors # Adds the blocked neighbors of the current cell to the closed_neighbors dictionary.

  rd.shuffle(dead_ends) # Randomly shuffles the dead_ends list.

  half_dead_ends = dead_ends[0 : len(dead_ends) // 2] # Selects the first half of the cells in the dead_ends list.

  for row, column in half_dead_ends: # For each cell in the half_dead_ends list:
    neighbors_to_choose = closed_neighbors[(row, column)] # Initializes a list to keep track of the cells that are closed neighbors of the current cell.
    random_cell = rd.randint(0, len(closed_neighbors[(row, column)]) - 1) # Randomly selects one of the cells in the neighbors_to_choose list.
    random, cell = neighbors_to_choose[random_cell] # Randomly selects one of the cells in the blocked neighbors of the current cell.
    ship_layout[random][cell] = 'O' # Marks the selected cell as open.

  return ship_layout # Returns the ship layout.

# Notation:

# 'B' = blocked
# 'O' = open
# 'F' = fire
# 'bot' = bot
# 'button' = button

def remove_fire_neighbors(ship_layout, neighbors): # Defines a function to remove fire neighbors from a list of neighbors.
  invalid = [] # Initializes a list to keep track of the cells that are invalid neighbors.
  
  for index in range(len(neighbors)): # For each cell in the neighbors list:
    row, column = neighbors[index] # Initializes the row and column of the current cell.

    if row > 0 and ship_layout[row - 1][column] == 'F': # If the top adjacent cell within the ship is on fire:
      invalid.append(index) # Adds the current cell to the invalid list.
      continue # Skips to the next cell.
    elif row < len(ship_layout) - 1 and ship_layout[row + 1][column] == 'F': # Else if the bottom adjacent cell within the ship is on fire:
      invalid.append(index) # Adds the current cell to the invalid list.
      continue # Skips to the next cell.
    elif column > 0 and ship_layout[row][column - 1] == 'F': # Else if the left adjacent cell within the ship is on fire:
      invalid.append(index) # Adds the current cell to the invalid list.
      continue # Skips to the next cell.
    elif column < len(ship_layout) - 1 and ship_layout[row][column + 1] == 'F': # Else if the right adjacent cell within the ship is on fire:
      invalid.append(index) # Adds the current cell to the invalid list.

  invalid.reverse() # Reverses the order of the invalid list so that the cells are removed in the correct order.

  for index in invalid: # For each cell in the invalid list:
    neighbors.pop(index) # Removes the cell from the neighbors list.

  return neighbors # Returns the updated neighbors list.

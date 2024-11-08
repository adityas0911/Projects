# Notation:

# 'B' = blocked
# 'O' = open
# 'F' = fire
# 'bot' = bot
# 'button' = button

def possible_neighbors(ship_layout, bot_position): # Defines a function to get the possible neighbors of the bot.
  neighbors = [] # Initializes an empty list to store the neighbors.
  row, column = bot_position # Extracts the row and column of the current bot position.

  if row > 0: # If the current cell is not in the top edge of the grid:
    if (ship_layout[row - 1][column] in {'O', 'button'}): # If the top adjacent cell is open or button:
      neighbors.append((row - 1, column)) # Adds the top adjacent cell to the neighbors list.
  if row < len(ship_layout) - 1: # If the current cell is not in the bottom edge of the grid:
    if (ship_layout[row + 1][column] in {'O', 'button'}): # If the bottom adjacent cell is open or button:
      neighbors.append((row + 1, column)) # Adds the bottom adjacent cell to the neighbors list.
  if column > 0: # If the current cell is not in the left edge of the grid:
    if (ship_layout[row][column - 1] in {'O', 'button'}): # If the left adjacent cell is open or button:
      neighbors.append((row, column - 1)) # Adds the left adjacent cell to the neighbors list.
  if column < len(ship_layout) - 1: # If the current cell is not in the right edge of the grid:
    if (ship_layout[row][column + 1] in {'O', 'button'}): # If the right adjacent cell is open or button:
      neighbors.append((row, column + 1)) # Adds the right adjacent cell to the neighbors list.

  return neighbors # Returns the list of neighbors.

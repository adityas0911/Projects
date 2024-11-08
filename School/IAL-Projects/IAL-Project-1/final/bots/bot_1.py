from functions import fire_spread

# Notation:

# 'B' = blocked
# 'O' = open
# 'F' = fire
# 'bot' = bot
# 'button' = button

def bot_1(ship_layout, bot_position, q, path): # Defines a function to increment the path of the bot 1.
  row, column = bot_position # Extracts the row and column of the current bot position.

  if path: # If the path is not empty:
    new_row, new_column = path[0] # Extracts the row and column of the next cell in the path.
  else: # Else:
    print('The shortest_path is empty.')

    return False, bot_position, path # Returns failure, bot_position, and path.

  if ship_layout[new_row][new_column] == 'button': # If the next cell in the path is the button:
    return True, (new_row, new_column), [] # Returns success, new bot position, and updated path.
  elif ship_layout[new_row][new_column] == 'F': # If the next cell in the path is fire:
    return False, (new_row, new_column), [] # Returns failure, new bot position, and updated path.
  else: # Else:
    ship_layout[row][column] = 'O' # Marks the current cell as open.
    ship_layout[new_row][new_column] = 'bot' # Marks the next cell as bot.

  fire_spreads = fire_spread.fire_spread(ship_layout, q) # Determines the cells that fire spreads to.

  path.pop(0) # Removes the current step from the path.

  return fire_spreads, (new_row, new_column), path # Returns the fire spread, new bot position, and updated path.

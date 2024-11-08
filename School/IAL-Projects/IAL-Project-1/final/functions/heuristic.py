# Notation:

# 'B' = blocked
# 'O' = open
# 'F' = fire
# 'bot' = bot
# 'button' = button

def heuristic(position, button_position, risk_map): # Heuristic function to estimate the distance from the current position to the button.
  manhattan_distance = abs(position[0] - button_position[0]) + abs(position[1] - button_position[1]) # Calculates the Manhattan distance from the current position to the button.
  risk_value = risk_map[position[0]][position[1]] # Gets the risk value at the current position.

  return manhattan_distance + risk_value # Returns the sum of the Manhattan distance and the risk at the current position.

import heapq
from collections import defaultdict

from functions import possible_neighbors

# Notation:

# 'B' = blocked
# 'O' = open
# 'F' = fire
# 'bot' = bot
# 'button' = button

def shortest_path(ship_layout, bot_position, button_position): # Defines a function to determine the shortest path from the bot to the button.
  fringe = [(0, bot_position)] # Initialize the fringe with the bot position and a distance of 0.
  parent = {} # Initialize the parent dictionary to reconstruct the path from the bot to the button.
  distance = defaultdict(lambda: float('inf')) # Initialize the distance dictionary with infinity for all cells except the bot's starting position.
  distance[bot_position] = 0 # Set the distance of the bot's starting position to 0.

  heapq.heapify(fringe) # Heapify the fringe to use it as a priority queue.

  while fringe: # While the fringe is not empty:
    current_distance, current_position = heapq.heappop(fringe) # Get the position with the smallest distance.

    if current_position == button_position: # If the current position is the button position:
      path = [] # Initializes the path list.

      while current_position in parent: # While the current position is in the parent dictionary:
        path.append(current_position) # Adds the current position to the path list.

        current_position = parent[current_position] # Sets the current position to the parent of the current position.

      path.reverse() # Reverse the path to get it from bot to button.

      return path # Returns the path.

    neighbors = possible_neighbors.possible_neighbors(ship_layout, current_position) # Get the possible neighbors of the current position.

    for neighbor in neighbors: # For each neighbor in the neighbors list:
      distance_to_neighbor = distance[current_position] + 1 # Calculates the distance to the neighbor.

      if distance[neighbor] > distance_to_neighbor: # If the distance to the neighbor is less than the current distance to the neighbor:
        distance[neighbor] = distance_to_neighbor # Updates the distance to the neighbor to the current distance to the neighbor.

        heapq.heappush(fringe, (distance_to_neighbor, neighbor)) # Pushes the neighbor to the fringe.

        parent[neighbor] = current_position # Set the current position as the parent of the neighbor.

  return False # Returns False if no path is found.

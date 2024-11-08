import pygame
import math
import os
import shutil
import atexit
import random as rd

from functions import ship_layout, bonus_ship_layout, shortest_path
from bots import bot_1, bot_2, bot_3, bot_4

# Notation:

# 'B' = blocked
# 'O' = open
# 'F' = fire
# 'bot' = bot
# 'button' = button

def main(): # Defines the main function.
  pygame.init() # Initializes pygame.

  bot_id = 1 # Initializes the ID of the bot as per the following: 1 = bot_1, 2 = bot_2, 3 = bot_3, 4 = bot_4.
  ship_id = 1 # Initializes the ID of the ship layout as per the following: 1 = ship_layout, 2 = bonus_ship_layout.
  steps = 10 # Initializes the number of steps to simulate the risk_map for bot_4.
  D = 80 # Initializes the dimension of the sqaure grid.
  q = 1 # Initializes the fire flammability.
  display_dimension = 900 # Initializes the dimension of the display.
  SCREEN_WIDTH = display_dimension # Initializes the width of the screen.
  SCREEN_HEIGHT = display_dimension # Initializes the height of the screen.
  SURFACE_WIDTH = math.ceil(SCREEN_WIDTH / D) # Initializes the width of the surface.
  SURFACE_HEIGHT = math.ceil(SCREEN_HEIGHT / D) # Initializes the height of the surface.

  # rd.seed(1) # Sets a seed value.

  if (D < 3): # If the dimension of the square grid is less than or equal to 3:
    return print("Invalid dimension.") # Returns an error message.
  if (q < 0 or q > 1): # If the fire flammability is not between 0 and 1:
    return print("Invalid flammability.") # Returns an error message.
  if (steps < 0): # If the number of steps is less than 0:
    return print("Invalid number of steps.") # Returns an error message.
  if (display_dimension <= 0): # If the width or height of the screen is less than or equal to 0:
    return print("Invalid screen size.") # Returns an error message.

  test_surface = pygame.Surface((SURFACE_WIDTH,SURFACE_HEIGHT)) # Initializes the surface object that goes on top of the display.
  screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT)) # Initializes the display.

  pygame.display.set_caption("Bot simulations") # Sets the title of the display.

  clock = pygame.time.Clock() # Initializes the time object.
  
  if ship_id == 1: # If the ID of the ship layout is 1:
    ship = ship_layout.ship_layout(D) # Initializes the ship layout.
  elif ship_id == 2: # If the ID of the ship layout is 2:
    ship = bonus_ship_layout.bonus_ship_layout(D) # Initializes the bonus ship layout.
  else: # Else:
    return print("Invalid ship layout ID.") # Returns an error message.

  SPLIT = SCREEN_HEIGHT / len(ship) # Initializes the height of the blocks.
  ship_surfaces = {(y * SPLIT, x * SPLIT): ship[x][y] for x in range(len(ship)) for y in range(len(ship))} # Initializes a dictionary to keep track of the blocks.

  open_cells = [] # Initializes a list to keep track of the open cells.

  for coordinates in ship_surfaces: # For each block in the ship layout:
    color = "black" if ship_surfaces[coordinates] == "B" \
    else "orchid" if ship_surfaces[coordinates] == "O" \
    else "orange" if ship_surfaces[coordinates] == 'F' else 'white' # Initializes the color of the block to be black if the block is blocked, orchid if the block is open, orange if the block is fire, and default white if the block is not blocked, open, or fire.

    test_surface.fill(color) # Fills the block with the color.
    screen.blit(test_surface, coordinates[0:2]) # Draws the block on the display.

    if color == "orchid": # If the block is open:
      open_cells.append(coordinates) # Adds the block to the open_cells list.

  rd.shuffle(open_cells) # Randomly shuffles the open_cells list.

  fire_location = open_cells[0] # Selects the first cell in the open_cells list as the fire location.
  bot_location = open_cells[1] # Selects the second cell in the open_cells list as the bot location.
  bot_position = (int(bot_location[1] // SPLIT), int(bot_location[0] // SPLIT)) # Initializes the position of the bot.
  button_location = open_cells[2] # Selects the third cell in the open_cells list as the button location.
  button_position = (int(button_location[1] // SPLIT), int(button_location[0] // SPLIT)) # Initializes the position of the button.

  test_surface.fill("orange") # Fills the fire block with orange.
  screen.blit(test_surface,fire_location[0:2]) # Draws the fire block on the display.

  ship[int(fire_location[1] // SPLIT)][int(fire_location[0] // SPLIT)] = 'F' # Draws the fire on the display.

  test_surface.fill("whitesmoke") # Fills the bot block with whitesmoke.
  screen.blit(test_surface,bot_location[0:2]) # Draws the bot block on the display.

  ship[bot_position[0]][bot_position[1]] = 'bot' # Draws the bot on the display.

  test_surface.fill("cyan1") # Fills the button block with cyan1.
  screen.blit(test_surface,button_location[0:2]) # Draws the button block on the display.

  ship[button_position[0]][button_position[1]] = 'button' # Draws the button on the display.
  path = shortest_path.shortest_path(ship, bot_position, button_position) # Initializes the path using the shortest_path function.
  run = True # Initializes the run variable.
  step_counter = 0 # Initializes the step counter variable.

  while run: # While the run variable is true:
    for event in pygame.event.get(): # For each event in the pygame event queue:
      if event.type == pygame.QUIT: # If the event is a quit event:
        run = False # Set the run variable to false.

        pygame.quit() # Quit the pygame library.

    pygame.display.update() # Update the display.

    if bot_id == 1: # If the ID of the bot is 1:
      new_fire_positions, new_bot_position, path = bot_1.bot_1(ship, bot_position, q, path) # Initializes the new fire positions, new robot position, and path for bot 1.
    elif bot_id == 2: # If the ID of the bot is 2:
      new_fire_positions, new_bot_position, path = bot_2.bot_2(ship, bot_position, button_position, q) # Initializes the new fire positions, new robot position, and path for bot 2.
    elif bot_id == 3: # If the ID of the bot is 3:
      new_fire_positions, new_bot_position, path = bot_3.bot_3(ship, bot_position, button_position, q) # Initializes the new fire positions, new robot position, and path for bot 3.
    elif bot_id == 4: # If the ID of the bot is 4:
      new_fire_positions, new_bot_position, path = bot_4.bot_4(ship, bot_position, button_position, q, steps) # Initializes the new fire positions, new robot position, and path for bot 4.
    else: # Else:
      return print("Invalid bot ID.") # Returns an error message.

    if (new_fire_positions == False or new_fire_positions == True or ship[button_position[0]][button_position[1]] == 'F'): # If the new fire positions are false or true or the button is fire:
      pygame.quit() # Quit the pygame library.

      run = False # Set the run variable to false.

      break # Break the loop.

    for x, y in new_fire_positions: # For each fire position in the new fire positions:
      ship_surfaces[(y * SPLIT, x * SPLIT)] = 'F' # Draw the fire on the display.

      ship[x][y] = 'F' # Draws the fire on the ship.

      test_surface.fill("orange") # Fills the fire block with orange.

      screen.blit(test_surface, (y * SPLIT, x * SPLIT)) # Draws the fire block on the display.

    x, y = bot_position # Initializes the x and y variables to the bot position.

    ship_surfaces[(y * SPLIT, x * SPLIT)] # Draws the open cells on the display.

    ship[x][y] = 'O' # Draws the open cells on the ship.

    test_surface.fill("orchid") # Fills the open cell block with orchid.

    screen.blit(test_surface, (y * SPLIT, x * SPLIT)) # Draws the open cell block on the display.

    x, y = new_bot_position # Initializes the x and y variables to the new bot position.

    ship_surfaces[(y * SPLIT, x * SPLIT)] # Draws the bot on the display.
    
    ship[x][y] = 'bot' # Draws the bot on the ship.

    test_surface.fill("whitesmoke") # Fills the bot block with whitesmoke.

    screen.blit(test_surface,(y * SPLIT, x * SPLIT)) # Draws the bot block on the display.

    bot_position = new_bot_position # Sets the bot position to the new bot position.

    pygame.time.wait(500) # Waits 0.5 seconds.

    step_counter += 1 # Increments the step counter.

    clock.tick(60) # Limits the frame rate to 60 frames per second.

  if new_fire_positions == False: # If the new fire positions are false:
    outcome = "Fire won." # Sets the outcome variable to fire won.
  elif ship[button_position[0]][button_position[1]] == 'F': # If the button is on fire:
    outcome = "Fire won." # Sets the outcome variable to fire won.
  elif new_bot_position == button_position: # If the new bot position is the button position:
    outcome = "Bot won." # Sets the outcome variable to bot won.
  else: # Else:
    outcome = "Tie occurred." # Sets the outcome variable to tie.

  print(f"Outcome: {outcome}")

  pygame.quit() # Quit the pygame library.

  run = False # Set the run variable to false.

def delete_pycache(): # Defines a function to delete the __pycache__ folders.
  try: # Tries to:
    subfolder_paths = [
      './bots/__pycache__',
      './functions/__pycache__'
    ] # Initializes the subfolder paths.

    for path in subfolder_paths: # For each subfolder path:
      if os.path.exists(path): # If the subfolder path exists:
        shutil.rmtree(path) # Deletes the subfolder.
        print(f"Deleted {path}.") # Prints that the subfolder was deleted.
      else: # Else:
        print(f"{path} was not found.") # Prints that the subfolder was not found.

  except Exception as e: # If an error occurs:
    print(f"Error deleting __pycache__ folders: {e}.") # Prints the error.

if __name__ == "__main__": # If the file is run directly:
  main() # Run the main function.
  atexit.register(delete_pycache) # Deletes the pycache folders.
